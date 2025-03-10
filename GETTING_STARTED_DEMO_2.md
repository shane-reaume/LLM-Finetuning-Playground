# Getting Started with LLM-Finetuning-Playground - Recipe Generation

**Recipe Generation** - A hands-on demo project for fine-tuning a small language model with LoRA adapters

## 🔍 Project Overview

This demo project demonstrates:

* **Model Architecture**: 
  * Fine-tuning a decoder-based **TinyLlama** (1.1B parameters) with LoRA adapters
  * Parameter-efficient fine-tuning with low-rank adaptation (LoRA)
  * Conditional text generation with ingredient-to-recipe formatting
  * Half-precision training (FP16) for memory efficiency

* **Training Methodology**:
  * Instruction fine-tuning on the RecipeNLG dataset 
  * Low-rank adapter training targeting key attention modules (q_proj, v_proj)
  * Efficient training with gradient accumulation and checkpointing
  * Memory optimization with offloading techniques for 8GB GPUs

* **Testing Framework**:
  * **Functional Tests**: Validating recipe generation from ingredient prompts
  * **Quality Assessment**: Measuring coherence and adherence to ingredients
  * **Memory Tests**: Ensuring model can run on consumer hardware
  * **Format Tests**: Verifying proper recipe structure in outputs
  * **Performance Benchmarks**: Tracking generation speed and throughput

* **Deployment Strategy**:
  * Export to **Ollama** for local inference without dependencies
  * LoRA adapter merging with base model for improved performance
  * Model quantization options for reduced memory footprint
  * Interactive CLI and web-based demo interfaces

## 🌟 Overview

This demo shows how to fine-tune a small language model to generate cooking recipes from ingredient lists. The process includes:

1. **Dataset preparation** - Download and process the RecipeNLG dataset
2. **Model fine-tuning** - Train TinyLlama with LoRA adapters
3. **Evaluation** - Test the model's performance
4. **Deployment** - Export to Ollama for local use

## 📋 Prerequisites

- **GPU with 8GB+ VRAM** recommended for training (CPU can be used but will be very slow)
- **Ollama** (optional, for local deployment) - [Install Ollama](https://ollama.ai/download)

## Recipe Generation Project

This project fine-tunes a small language model (TinyLlama) to generate recipes from ingredient lists. Here's how to use it:

### Step 1: Download the Recipe Dataset

Unlike the sentiment analysis project, the recipe generation model requires a dataset that must be manually downloaded:

```bash
# Create directory for the dataset
mkdir -p ~/recipe_manual_data

# Visit the official website and download the dataset
# https://recipenlg.cs.put.poznan.pl/dataset

# After downloading, place full_dataset.csv in your recipe_manual_data directory
```

The dataset can be found at the official project website: [https://recipenlg.cs.put.poznan.pl/dataset](https://recipenlg.cs.put.poznan.pl/dataset)

> **Note:** The dataset is approximately 600MB in size and contains over 2 million recipes.

### Step 2: Prepare the Dataset

After downloading the dataset, prepare it for training:

```bash
# Specify the data directory when running the command
python -m src.data.recipe_prepare_dataset --data_dir ~/recipe_manual_data
```

Alternatively, use the Makefile:

```bash
# For the manually downloaded dataset
make recipe-data CONFIG=config/text_generation.yaml DATA_DIR=~/recipe_manual_data
```

This processes recipe data and creates test examples at `data/processed/recipe_test_examples.json`. 

The configuration file (`config/text_generation.yaml`) controls the dataset processing parameters and output locations.

### Step 3: Train the Model

#### Check your hardware configuration

You can get a report on your operating system and hardware configuration by running the `config_optimizer.py` script to see if it is optimized for training a model of this size:

```bash
python scripts/config_optimizer.py --config config/text_generation.yaml
```

If you want to optimize the configuration for your hardware, you can run the `config_optimizer.py` script with the `-o` flag to save the optimized configuration to a new file:

```bash
python scripts/config_optimizer.py --config config/text_generation_optimized.yaml --update
```

Before running the full training process (which can take 2-4 hours), you may want to perform a quick sanity test to ensure everything is configured correctly:

#### Option A: Run a Quick Sanity Test (Recommended)

```bash
# Run a minimal training session for testing purposes
make recipe-train-test DATA_DIR=~/recipe_manual_data
```

This will:

- Process only 30 training examples
- Train for just 1% of an epoch
- Use reduced sequence lengths (32 tokens)
- Complete in a few minutes rather than hours

If the sanity test runs successfully, you can proceed with the full training.

> **Troubleshooting Memory Issues**: If you encounter a "CUDA out of memory" error, your GPU may not have enough VRAM. Try these solutions:
> 
> **Option 1: Further reduce memory usage**
> 1. Edit `config/text_generation_sanity_test.yaml` and reduce `batch_size` to 1 (already set)
> 2. Further reduce `max_length` to 16 (currently 32)
> 3. Reduce `max_train_samples` to 20 (currently 30)
>
> **Option 2: Use memory optimization techniques**
> 1. Make sure the LoRA configuration has `"offload_modules": true` (already set)
> 2. Consider adding `"8bit_adam": true` to the config if using PyTorch >= 2.0
> 3. Set PyTorch memory allocation configuration with:
>    ```bash
>    export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32,garbage_collection_threshold:0.6
>    ```
>
> **Option 3: Run on CPU instead**
> If all else fails, run the CPU version of the sanity test (very slow but works on any machine):
> ```bash
> make recipe-train-test-cpu DATA_DIR=~/recipe_manual_data
> ```
>
> **Option 4: Cloud GPUs**
> Consider using a cloud GPU service like Google Colab, Kaggle, or AWS with more VRAM.

#### Option B: Run Full Training with Optimized Configuration

Start the training process with a LoRA adapter:

```bash
# Run the full training process
make recipe-train-optimized DATA_DIR=~/recipe_manual_data
```

#### Option C: Run Full Training with Original Configuration

Start the training process with a LoRA adapter:

```bash
# Run the full training process
make recipe-train DATA_DIR=~/recipe_manual_data
```

This will:

- Download the TinyLlama base model
- Set up the LoRA training configuration
- Fine-tune the model on recipe generation
- Save the model to `models/recipe_assistant`

Training typically takes 2-4 hours on a good GPU.

> **Memory Requirements**: For full training, we recommend a GPU with at least 16GB VRAM.
> For smaller GPUs (8GB), use our low-memory configuration:
> ```bash
> make recipe-train-low-memory DATA_DIR=~/recipe_manual_data
> ```
> 
> The low-memory configuration makes the following changes:
> 1. Reduces sequence length from 512 to 256 tokens
> 2. Uses batch size of 1 with gradient accumulation of 8
> 3. Enables gradient checkpointing and 8-bit optimizer
> 4. Uses CPU offloading for LoRA modules
> 5. Reduces the LoRA rank from 8 to 4
>
> If you still encounter memory issues, try reducing the dataset size by adding:
> ```yaml
> data:
>   max_train_samples: 50000  # Use 50k samples instead of the full dataset
> ```
> to your configuration file.

### Step 4: Evaluate the Model

Assess the model's performance:

```bash
# Basic evaluation command
python -m src.model.recipe_evaluate --config config/text_generation.yaml

# Or with the Makefile
make recipe-evaluate
```

This will generate sample recipes and evaluate:

- Generation quality
- Recipe formatting
- Ingredient usage
- Runtime performance

### Step 5: Try the Interactive Demos

Once your model is trained, you can use two different demo interfaces:

#### CLI Demo
```bash
# Run the command-line interface demo
python -m src.recipe_demo --model_dir="models/recipe_assistant"
```

This demo provides a command-line interface where you can enter ingredients and get formatted recipes.

#### Web UI Demo
```bash
# Run the web interface demo
python -m src.recipe_web_demo --model_dir="models/recipe_assistant"
```

The web UI demo launches a Gradio interface in your browser, allowing for:

- Entering ingredients to generate recipes
- Adjusting generation parameters
- Seeing formatted recipe outputs

### Step 6 (Optional): Deploy to Ollama

If you have Ollama installed, you can export your model for easy local deployment:

```bash
python -m src.model.recipe_export_to_ollama --model_dir="models/recipe_assistant" --model_name="recipe-gen"
```

Alternatively, use the Makefile target:

```bash
make recipe-export
```

Then run your model with:

```bash
ollama run recipe-gen
```

## 🚀 Hardware Optimization and Memory Management

Training LLMs can be resource-intensive, even with smaller models like TinyLlama. This project includes several tools to help you optimize your training process based on your hardware capabilities.

### Hardware Analysis and Configuration Optimization

The `config_optimizer.py` script analyzes your hardware and recommends optimal configuration settings:

```bash
# Display hardware information and recommendations
python scripts/config_optimizer.py

# Analyze hardware and update a specific config
python scripts/config_optimizer.py --config config/text_generation.yaml --update

# Generate an optimized config without modifying the original
python scripts/config_optimizer.py --config config/text_generation.yaml --output config/my_optimized_config.yaml
```

### GPU Memory Optimization

For more detailed GPU memory analysis and optimization:

```bash
# Display memory statistics and recommendations
python scripts/optimize_gpu_memory.py

# Run a memory test to find max allocation
python scripts/optimize_gpu_memory.py --test

# Show only memory statistics
python scripts/optimize_gpu_memory.py --stats
```

### Real-time Memory Monitoring During Training

You can monitor GPU memory usage during training by adding a few lines to your training script:

```python
from src.utils.memory_monitor import GPUMemoryMonitor

# Create and start the monitor before training
memory_monitor = GPUMemoryMonitor(interval_seconds=30)
memory_monitor.start()

# ... training code ...

# Stop the monitor when done
memory_monitor.stop()
```

### Available Configuration Files

We provide several pre-configured YAML files for different hardware scenarios:

1. **Standard Configuration** (`config/text_generation.yaml`):
   - Default settings for GPUs with 16GB+ VRAM
   - Full sequence length (512 tokens)
   - Batch size of 2 with large gradient accumulation

2. **Optimized Configuration** (`config/text_generation_optimized.yaml`):
   - Balanced settings for most GPUs (10GB+ VRAM)
   - Reduced sequence length (256 tokens)
   - Smaller gradient accumulation steps
   - Limited dataset size (100,000 samples)

3. **Memory-Optimized Configuration** (`config/text_generation_optimized_memory.yaml`):
   - Settings for GPUs with limited VRAM (8-12GB)
   - Aggressive memory optimizations
   - Gradient checkpointing enabled
   - Additional performance settings

4. **Low-Memory Configuration** (`config/text_generation_low_memory.yaml`):
   - For GPUs with very limited VRAM (6-8GB)
   - Minimal batch size with CPU offloading
   - Reduced model parameters

5. **Sanity Test Configuration** (`config/text_generation_sanity_test.yaml`):
   - For quick testing only (all GPUs)
   - Minimal dataset size (30 examples)
   - Very short sequence length (32 tokens)
   - Trains for just 1% of an epoch

### Choosing the Right Configuration

The best approach is to:

1. Run the `config_optimizer.py` script to analyze your hardware
2. Select a configuration that matches your hardware capabilities
3. Use the memory monitor during training to check utilization
4. Adjust batch size and sequence length if you encounter memory issues

For most modern consumer GPUs (8GB+ VRAM), the optimized configuration should work well:

```bash
make recipe-train-optimized DATA_DIR=~/recipe_manual_data
```

For high-end GPUs with 12GB+ VRAM, try the memory-optimized configuration for better performance:

```bash
make recipe-train-high-memory DATA_DIR=~/recipe_manual_data
```

## Project Structure for Recipe Generation

- `config/text_generation.yaml`: Configuration file for training and evaluation
- `config/text_generation_sanity_test.yaml`: Configuration for quick sanity testing
- `config/text_generation_low_memory.yaml`: Configuration for low-memory training
- `config/recipe_prompt.txt`: Template for recipe formatting
- `src/data/recipe_prepare_dataset.py`: Dataset preparation script
- `src/model/recipe_train.py`: Training script
- `src/model/recipe_evaluate.py`: Evaluation script
- `src/recipe_demo.py`: CLI demo interface
- `src/recipe_web_demo.py`: Web UI demo interface
- `src/model/recipe_export_to_ollama.py`: Ollama deployment utilities
- `tests/test_recipe_model.py`: Test suite
- `data/processed/recipe_test_examples.json`: Test examples for evaluation
- `models/recipe_assistant/`: Directory for the trained model checkpoints

## Customization

You can modify the configuration files to change how the recipe generation model works:

### Main Configuration File (`config/text_generation.yaml`):

- **Data Settings**:
  - `dataset_name`: The dataset to use (default: "recipe_nlg")
  - `cache_dir`: Where processed data is stored (`./data/processed/generation`)
  - `max_length`: Maximum sequence length (default: 512)
  - `max_train_samples`: Optional limit on training examples (for testing)

- **Model Settings**:
  - `name`: Base model to fine-tune (default: "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
  - `save_dir`: Where to save the trained model (`./models/recipe_assistant`)

- **Training Settings**:
  - Learning parameters (batch size, learning rate, etc.)
  - LoRA configuration (rank, alpha, target modules)
  - `gradient_checkpointing`: Reduces memory usage but slows training
  - `fp16`: Uses half-precision for better performance

- **Testing Settings**:
  - `test_examples_file`: Path to test examples (`data/processed/recipe_test_examples.json`)
  - Generation parameters (temperature, top_p, etc.)

### Low Memory Configuration (`config/text_generation_low_memory.yaml`):

This configuration is optimized for GPUs with limited VRAM (8GB):
  - Reduces sequence length from 512 to 256 tokens
  - Uses batch size of 1 with gradient accumulation of 8
  - Enables gradient checkpointing and 8-bit optimizer
  - Uses CPU offloading for LoRA modules
  - Reduces the LoRA rank from 8 to 4

### Sanity Test Configuration (`config/text_generation_sanity_test.yaml`):

This is a minimal version of the main configuration designed for quick testing:
  - Uses only 30 training examples
  - Trains for just 1% of an epoch
  - Uses much shorter sequence lengths (32 tokens)
  - Employs memory optimizations like gradient checkpointing
  - Uses a smaller batch size to reduce memory requirements
  - Saves output to a different directory (`./models/recipe_assistant_test`)

### Recipe Prompt Template (`config/recipe_prompt.txt`):

You can edit this file to change how recipes are formatted during generation.

Editing these files allows you to experiment with:

- Different base models
- LoRA adapter settings
- Training parameters
- Generation parameters (temperature, top-p, etc.)

## Advanced Usage

### Merging LoRA Adapter with Base Model

For better performance or offline use, you can merge the LoRA adapter with the base model:

```bash
python -m src.model.recipe_merge_and_export_lora --base_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0" --lora_model="models/recipe_assistant" --output_dir="models/recipe_merged"
```

### Performance Optimization

If you're experiencing slow generation speeds, try:

1. Reducing the context length in the configuration file
2. Using a smaller base model
3. Enabling 8-bit quantization during inference
4. Deploying to Ollama with optimized parameters

## Next Steps

Once you're comfortable with the recipe generation project, consider:

1. **Enhancing the prompts** - Create better system prompts and templates
2. **Fine-tuning on different domains** - Try other cooking styles or cuisines
3. **Improving evaluation metrics** - Develop better ways to assess generation quality
4. **Exploring model merging** - Learn more about model merging techniques
5. **Trying our sentiment analysis demo** - Check GETTING_STARTED_DEMO_1.md

## Testing

Testing is a critical aspect of model development. The recipe generation model can be tested using:

```bash
# Run the recipe model tests
pytest tests/test_recipe_model.py -v

# Generate coverage report
pytest --cov=src --cov-report=html
```

The HTML coverage report will be generated in the `htmlcov/` directory and can be viewed in a browser.

For a comprehensive guide to our testing philosophy, methodology, and approach to ML model testing, please refer to the detailed testing documentation in [GETTING_STARTED_DEMO_1.md](GETTING_STARTED_DEMO_1.md#testing-philosophy-and-methodology).

## Training the Recipe Generator Model

To train the model, first make sure you have processed the data using the steps above. Then run:

```bash
make recipe-train DATA_DIR=~/recipe_manual_data
```

This will train the recipe generation model according to the configuration in `config/text_generation.yaml`. Training this small model will usually take 4-6 hours on a consumer GPU with 16GB of VRAM. The process will save checkpoints to the location specified in the config file.

### Memory-Optimized Training Options

We provide several training configurations to accommodate different GPU memory constraints:

1. **Standard Training** (16GB+ VRAM recommended):
   ```bash
   make recipe-train DATA_DIR=~/recipe_manual_data
   ```

2. **Medium-Memory Training** (8GB+ VRAM, faster than low-memory):
   ```bash
   make recipe-train-medium-memory DATA_DIR=~/recipe_manual_data
   ```
   - Uses a balanced approach with memory savings but better speed
   - Trains on 100,000 examples instead of the full dataset
   - Expected training time: 2-3 hours

3. **Low-Memory Training** (6GB+ VRAM):
   ```bash
   make recipe-train-low-memory DATA_DIR=~/recipe_manual_data
   ```
   - Uses aggressive memory optimizations including CPU offloading
   - Significantly slower than standard training
   - Expected training time: 8-10 hours

Choose the option that best matches your hardware capabilities. The medium-memory option provides a good balance between memory efficiency and training speed.

### Quick Sanity Test

```bash
# Run a minimal training session for testing purposes
make recipe-train-test DATA_DIR=~/recipe_manual_data
```

This will:
- Process only 30 training examples
- Train for just 1% of an epoch
- Use reduced sequence lengths (32 tokens)
- Complete in a few minutes rather than hours

If the sanity test runs successfully, you can proceed with the full training.
