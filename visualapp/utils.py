from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import re

def translate_text(input_text, target_lang):
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

    tokenizer.src_lang = "en_XX"
    tokenizer.tgt_lang = target_lang

    max_length = 50000
    MAX_LENGTH=50000

    
    encoded_text = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)

    generated_tokens = model.generate(
        **encoded_text,
        forced_bos_token_id=tokenizer.lang_code_to_id[target_lang]
    )
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

    return translated_text