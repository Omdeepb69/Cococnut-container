from typing import Optional, List
from config import config

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
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

        # Precision Optimization
        if self.device == "cuda":
            self.dtype = torch.float16  # standard for GPUs
        else:
            self.dtype = torch.float32  # safest for CPU

        print(f"Loading S-Tier Engine: {self.model_id} on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            
            load_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": self.dtype,
            }
            
            # Use device_map only if GPU is present for multi-GPU efficiency
            if self.device == "cuda":
                load_kwargs["device_map"] = "auto"
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                **load_kwargs
            )
            
            if self.device != "cuda":
                self.model = self.model.to(self.device)
                
            print(f"Model {self.model_id} loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")

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
            if self.device == "cuda":
                with torch.autocast(device_type=self.device, dtype=self.dtype):
                    outputs = self.model.generate(
                        input_ids=inputs["input_ids"],
                        attention_mask=inputs["attention_mask"],
                        max_new_tokens=150,
                        temperature=0.3,
                        repetition_penalty=1.2,
                        do_sample=True,
                        eos_token_id=self.tokenizer.eos_token_id,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
            else:
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_new_tokens=150,
                    temperature=0.3,
                    repetition_penalty=1.2,
                    do_sample=True,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.eos_token_id
                )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        return response
