import spacy
import langid
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Define the directory for spaCy models
spacy_model_dir_path = Path('data/spacy_models')
spacy_model_dir_path.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

# Restrict langid to English and Chinese
langid.set_languages(['en', 'zh'])

# Define paths to spaCy models
model_paths = {
    'en': spacy_model_dir_path / 'en_core_web_lg-3.8.0/en_core_web_lg/en_core_web_lg-3.8.0',
    'zh': spacy_model_dir_path / 'zh_core_web_lg-3.8.0/zh_core_web_lg/zh_core_web_lg-3.8.0'
}

# Load spaCy models from local directories
ner_models = {}
for lang, model_path in model_paths.items():
    if not model_path.exists():
        logging.error(f"Model for '{lang}' not found at {model_path}. Ensure the model is downloaded.")
        continue  # Skip loading if model is missing

    try:
        ner_models[lang] = spacy.load(model_path)
        logging.info(f"Loaded {lang} model from {model_path}")
    except Exception as e:
        logging.error(f"Error loading {lang} model from {model_path}: {e}")

# Define the labels of interest
interested_labels = {'PERSON', 'GPE', 'LOC', 'PRODUCT', 'ORG', 'EVENT', 'WORK_OF_ART', 'FAC', 'LANGUAGE', 'NORP'}

def detect_language(text: str) -> str:
    """Detect language of input text."""
    try:
        return langid.classify(text)[0]
    except Exception as e:
        logging.error(f"Language detection failed: {e}")
        return 'en'  # Default to English on failure

def extract_entities(text: str) -> list[str]:
    """Extract named entities from text."""
    lang = detect_language(text) if len(text) >= 10 else 'en'

    if lang not in ner_models:
        logging.warning(f"No NER model available for language '{lang}', defaulting to English.")
        lang = 'en'

    doc = ner_models[lang](text)
    return [ent.text for ent in doc.ents if ent.label_ in interested_labels]
