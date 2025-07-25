import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image, ImageDraw, ImageFilter
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlantClassifierTrainer:
    def __init__(self):
        self.model = None
        self.img_height = 224
        self.img_width = 224
        self.batch_size = 32
        
    def create_synthetic_dataset(self, num_samples_per_class=500):
        """Create synthetic plant leaf dataset for demonstration"""
        logger.info("Creating synthetic dataset...")
        
        # Create directories
        os.makedirs('data/train/healthy', exist_ok=True)
        os.makedirs('data/train/diseased', exist_ok=True)
        os.makedirs('data/validation/healthy', exist_ok=True)
        os.makedirs('data/validation/diseased', exist_ok=True)
        
        # Generate synthetic healthy leaves
        self._generate_synthetic_leaves('data/train/healthy', num_samples_per_class, 'healthy')
        self._generate_synthetic_leaves('data/validation/healthy', num_samples_per_class // 5, 'healthy')
        
        # Generate synthetic diseased leaves  
        self._generate_synthetic_leaves('data/train/diseased', num_samples_per_class, 'diseased')
        self._generate_synthetic_leaves('data/validation/diseased', num_samples_per_class // 5, 'diseased')
        
        logger.info("Synthetic dataset created successfully")
    
    def _generate_synthetic_leaves(self, output_dir, num_samples, leaf_type):
        """Generate synthetic leaf images"""
        for i in range(num_samples):
            # Create base leaf image
            img = Image.new('RGB', (self.img_width, self.img_height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Create leaf shape
            self._draw_leaf_shape(draw, leaf_type)
            
            # Add noise and variations
            img = self._add_image_variations(img, leaf_type)
            
            # Save image
            filename = f'{leaf_type}_leaf_{i:04d}.png'
            img.save(os.path.join(output_dir, filename))
    
    def _draw_leaf_shape(self, draw, leaf_type):
        """Draw a basic leaf shape"""
        # Define leaf parameters
        center_x, center_y = self.img_width // 2, self.img_height // 2
        leaf_width = random.randint(80, 120)
        leaf_height = random.randint(120, 160)
        
        # Base green color for healthy leaves
        if leaf_type == 'healthy':
            base_color = (34, 139, 34)  # Forest green
            color_variation = 30
        else:
            base_color = (107, 142, 35)  # Olive drab (less healthy)
            color_variation = 40
        
        # Add color variation
        r = max(0, min(255, base_color[0] + random.randint(-color_variation, color_variation)))
        g = max(0, min(255, base_color[1] + random.randint(-color_variation, color_variation)))
        b = max(0, min(255, base_color[2] + random.randint(-color_variation, color_variation)))
        leaf_color = (r, g, b)
        
        # Draw leaf shape (oval)
        left = center_x - leaf_width // 2
        top = center_y - leaf_height // 2
        right = center_x + leaf_width // 2
        bottom = center_y + leaf_height // 2
        
        draw.ellipse([left, top, right, bottom], fill=leaf_color)
        
        # Add leaf vein
        vein_color = tuple(max(0, c - 20) for c in leaf_color)
        draw.line([center_x, top + 10, center_x, bottom - 10], fill=vein_color, width=2)
        
        # Add side veins
        for i in range(3):
            offset = (i + 1) * 20
            draw.line([center_x, center_y - offset, center_x + 30, center_y - offset + 15], 
                     fill=vein_color, width=1)
            draw.line([center_x, center_y + offset, center_x - 30, center_y + offset - 15], 
                     fill=vein_color, width=1)
    
    def _add_image_variations(self, img, leaf_type):
        """Add variations to make images more realistic"""
        # Convert to array for manipulation
        img_array = np.array(img)
        
        # Add disease markers for diseased leaves
        if leaf_type == 'diseased':
            img = self._add_disease_markers(img)
        
        # Add slight blur for realism
        if random.random() > 0.7:
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Add brightness variation
        enhancer = tf.keras.utils.img_to_array(img)
        enhancer = enhancer * random.uniform(0.8, 1.2)
        enhancer = np.clip(enhancer, 0, 255)
        img = tf.keras.utils.array_to_img(enhancer)
        
        return img
    
    def _add_disease_markers(self, img):
        """Add disease markers to leaf images"""
        draw = ImageDraw.Draw(img)
        
        # Add brown spots for disease
        num_spots = random.randint(2, 8)
        for _ in range(num_spots):
            x = random.randint(50, self.img_width - 50)
            y = random.randint(50, self.img_height - 50)
            radius = random.randint(5, 15)
            
            # Brown/yellow disease colors
            disease_colors = [(139, 69, 19), (218, 165, 32), (160, 82, 45), (255, 140, 0)]
            color = random.choice(disease_colors)
            
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
        
        # Add some yellowing
        if random.random() > 0.5:
            overlay = Image.new('RGB', img.size, (255, 255, 0))
            img = Image.blend(img, overlay, 0.1)
        
        return img
    
    def build_model(self):
        """Build the CNN model for binary classification"""
        logger.info("Building model...")
        
        self.model = models.Sequential([
            layers.Rescaling(1./255, input_shape=(self.img_height, self.img_width, 3)),
            
            # First convolutional block
            layers.Conv2D(32, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Second convolutional block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Third convolutional block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Fourth convolutional block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Flatten and dense layers
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        # Compile model
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Model built successfully")
        return self.model
    
    def prepare_data(self):
        """Prepare data generators"""
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Only rescaling for validation
        validation_datagen = ImageDataGenerator(rescale=1./255)
        
        # Create data generators
        train_generator = train_datagen.flow_from_directory(
            'data/train',
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='binary'
        )
        
        validation_generator = validation_datagen.flow_from_directory(
            'data/validation',
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='binary'
        )
        
        return train_generator, validation_generator
    
    def train_model(self, epochs=10):
        """Train the model"""
        logger.info("Starting model training...")
        
        # Prepare data
        train_generator, validation_generator = self.prepare_data()
        
        # Define callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=3,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=2,
                min_lr=0.0001
            )
        ]
        
        # Train model
        history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=validation_generator,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Model training completed")
        return history
    
    def save_model(self, filepath='models/plant_classifier.h5'):
        """Save the trained model"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def evaluate_model(self):
        """Evaluate model performance"""
        if self.model is None:
            logger.error("No model to evaluate")
            return None
        
        _, validation_generator = self.prepare_data()
        
        # Evaluate on validation set
        loss, accuracy = self.model.evaluate(validation_generator, verbose=0)
        logger.info(f"Validation Accuracy: {accuracy:.4f}")
        logger.info(f"Validation Loss: {loss:.4f}")
        
        return {'accuracy': accuracy, 'loss': loss}

def main():
    """Main training function"""
    trainer = PlantClassifierTrainer()
    
    # Create synthetic dataset
    trainer.create_synthetic_dataset(num_samples_per_class=200)
    
    # Build model
    trainer.build_model()
    
    # Train model
    trainer.train_model(epochs=5)  # Small number for demo
    
    # Evaluate model
    trainer.evaluate_model()
    
    # Save model
    trainer.save_model()
    
    logger.info("Training completed successfully!")

if __name__ == "__main__":
    main()