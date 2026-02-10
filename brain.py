from threading import Thread
from typing import Optional, List, Generator
from config import config

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextIteratorStreamer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class ModelEngine:
    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or config.MODEL_ID
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self.dtype = torch.float32
        self.inference_count = 0

    def load_model(self):
        if not TRANSFORMERS_AVAILABLE:
            print("WARNING: Transformers/Torch not installed. Running in MOCK mode.")
            return

        # Hardware Auto-Detection
        if config.DEVICE == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = config.DEVICE

        # Precision Optimization (FP16 vs BF16 vs FP32)
        if self.device == "cuda":
            # BF16 is superior for Ampere (RTX 30 series, A100) and later
            if torch.cuda.get_device_capability()[0] >= 8:
                print("Ampere+ Architecture detected. Using BF16 for maximum stability.")
                self.dtype = torch.bfloat16
            else:
                self.dtype = torch.float16
        else:
            self.dtype = torch.float32

        print(f"Loading S-Tier Engine: {self.model_id} on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            
            load_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": self.dtype,
            }

            # Quantization Logic
            if self.device == "cuda":
                load_kwargs["device_map"] = "auto"
                if config.LOAD_IN_4BIT:
                    print("Enabling 4-bit Quantization (NF4)...")
                    load_kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=self.dtype, # Match the auto-sensed dtype
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True
                    )
                elif config.LOAD_IN_8BIT:
                    print("Enabling 8-bit Quantization...")
                    load_kwargs["load_in_8bit"] = True
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                **load_kwargs
            )
            
            if self.device != "cuda" and not (config.LOAD_IN_4BIT or config.LOAD_IN_8BIT):
                self.model = self.model.to(self.device)
                
            print(f"Model {self.model_id} loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")

    @property
    def ready(self) -> bool:
        return self.model is not None

    def get_model_hash(self) -> str:
        """Returns a stable hash of the model ID for cache versioning."""
        import hashlib
        return hashlib.md5(self.model_id.encode()).hexdigest()[:8]

    def predict(self, prompt: str, history: list = None) -> str:
        self.inference_count += 1
        if not TRANSFORMERS_AVAILABLE or not self.model:
            return f"Error: Model not loaded. Ensure heavy dependencies are installed."

        messages = history if history else []
        messages.append({"role": "user", "content": prompt})

        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        ).to(self.device)

        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.3,
                repetition_penalty=1.2,
                do_sample=True,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        return response

    def stream_predict(self, prompt: str, history: list = None) -> Generator[str, None, None]:
        """Real-time token streaming for Gonyai Production UX."""
        self.inference_count += 1
        if not TRANSFORMERS_AVAILABLE or not self.model:
            yield "Error: Model not loaded."
            return

        messages = history if history else []
        messages.append({"role": "user", "content": prompt})

        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        ).to(self.device)

        streamer = TextIteratorStreamer(self.tokenizer, timeout=10.0, skip_prompt=True, skip_special_tokens=True)
        
        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=512,
            temperature=0.3,
            do_sample=True,
            repetition_penalty=1.2,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id
        )

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            yield new_text
