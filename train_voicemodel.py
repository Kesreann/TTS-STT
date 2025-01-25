import os
import json
import shutil
import TTS.configs.shared_configs as XttsConfig
import TTS.configs.xtts_config as BaseDatasetConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.audio import AudioProcessor
from TTS.tts.utils.text.tokenizer import TTSTokenizer
import torch

# ---- CONFIGURATION ----
DATASET_PATH = "dataset/"  # Folder containing metadata.csv and audio files
OUTPUT_MODEL_DIR = "modelfiles/custom_xtts"  # Where the trained model is saved
EPOCHS = 50  # Training duration
BATCH_SIZE = 8  # Reduce if GPU memory is limited
LEARNING_RATE = 1e-4  # Learning rate for model training
USE_CUDA = torch.cuda.is_available()
DEVICE = "cuda" if USE_CUDA else "cpu"

# Ensure output directory exists
os.makedirs(OUTPUT_MODEL_DIR, exist_ok=True)

# ---- CREATE XTTS CONFIGURATION ----
config = XttsConfig()
config.output_path = OUTPUT_MODEL_DIR
config.dataset = BaseDatasetConfig(
    formatter="ljspeech",  # Standard format for datasets
    dataset_path=DATASET_PATH,
)
config.num_epochs = EPOCHS
config.batch_size = BATCH_SIZE
config.learning_rate = LEARNING_RATE
config.compute_f0 = True  # XTTS uses pitch information
config.num_loader_workers = 4

# Save config to model directory
with open(os.path.join(OUTPUT_MODEL_DIR, "config.json"), "w") as f:
    json.dump(config.to_dict(), f, indent=4)

# ---- INITIALIZE AUDIO PROCESSOR ----
ap = AudioProcessor.init_from_config(config)

# ---- INITIALIZE TOKENIZER ----
tokenizer, config = TTSTokenizer.init_from_config(config)

# ---- INITIALIZE XTTS MODEL ----
print("Initializing XTTS model...")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_path=None, eval=False)
model.to(DEVICE)

# ---- START TRAINING ----
print("Starting training...")
model.train_loop(config, ap, tokenizer)

# ---- SAVE TRAINED MODEL ----
checkpoint_path = os.path.join(OUTPUT_MODEL_DIR, "custom_xtts.pth")
torch.save(model.state_dict(), checkpoint_path)
print(f"Training complete! Model saved at: {checkpoint_path}")
