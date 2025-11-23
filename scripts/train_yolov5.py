"""
YOLOv5n Training Script for Fruit Ripeness Detection
Trains YOLOv5n model on 15-class fruit ripeness dataset using Ultralytics.
Supports pause/resume functionality - press Ctrl+C to pause, then resume later.
"""

from ultralytics import YOLO
import torch
import signal
import sys
import os
from pathlib import Path

# Global flag to track if training was paused
training_paused = False
checkpoint_path = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully to pause training"""
    global training_paused, checkpoint_path
    print("\n\n" + "=" * 60)
    print("Training paused by user (Ctrl+C)")
    print("=" * 60)
    
    # The Ultralytics YOLO train() method automatically saves checkpoints
    # The last checkpoint will be saved at: runs/train/yolov5n_fruit_ripeness/weights/last.pt
    checkpoint_path = 'runs/train/yolov5n_fruit_ripeness/weights/last.pt'
    
    if os.path.exists(checkpoint_path):
        print(f"\nCheckpoint saved at: {checkpoint_path}")
        print("\nTo resume training, run:")
        print(f"  python train_yolov5.py --resume {checkpoint_path}")
        print("\nOr simply run:")
        print(f"  python train_yolov5.py --resume")
        print("  (will automatically use the last checkpoint)")
    else:
        print("\nWarning: Checkpoint not found yet. Training may not have saved a checkpoint.")
        print("Wait a moment and check: runs/train/yolov5n_fruit_ripeness/weights/")
    
    training_paused = True
    sys.exit(0)

def find_latest_checkpoint():
    """Find the latest checkpoint file"""
    checkpoint_dir = Path('runs/train/yolov5n_fruit_ripeness/weights')
    
    if not checkpoint_dir.exists():
        return None
    
    # Check for last.pt first (most recent)
    last_pt = checkpoint_dir / 'last.pt'
    if last_pt.exists():
        return str(last_pt)
    
    # Otherwise, find the most recent checkpoint
    checkpoints = list(checkpoint_dir.glob('*.pt'))
    if checkpoints:
        # Sort by modification time, most recent first
        checkpoints.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return str(checkpoints[0])
    
    return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Train YOLOv5n model with pause/resume support')
    parser.add_argument('--resume', type=str, nargs='?', const=True, default=None,
                        help='Resume training from checkpoint. If no path provided, uses latest checkpoint.')
    parser.add_argument('--epochs', type=int, default=60, help='Number of training epochs')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    parser.add_argument('--imgsz', type=int, default=640, help='Image size')
    parser.add_argument('--data', type=str, default='../data/datasets/Fruit_dataset/data.yaml', help='Dataset config file')
    parser.add_argument('--project', type=str, default='runs/train', help='Project directory')
    parser.add_argument('--name', type=str, default='yolov5n_fruit_ripeness', help='Experiment name')
    
    args = parser.parse_args()
    
    # Register signal handler for graceful pause
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 60)
    print("YOLOv5n Fruit Ripeness Detection Training")
    print("=" * 60)
    
    # Check CUDA availability
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nDevice: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    print()
    
    # Determine if resuming or starting fresh
    resume_path = None
    if args.resume:
        if args.resume is True:
            # Auto-find latest checkpoint
            resume_path = find_latest_checkpoint()
            if resume_path:
                print(f"Resuming from latest checkpoint: {resume_path}")
            else:
                print("No checkpoint found. Starting fresh training.")
                resume_path = None
        else:
            # Use provided checkpoint path
            resume_path = args.resume
            if os.path.exists(resume_path):
                print(f"Resuming from checkpoint: {resume_path}")
            else:
                print(f"Warning: Checkpoint not found at {resume_path}")
                print("Starting fresh training.")
                resume_path = None
    
    # Load model
    if resume_path and os.path.exists(resume_path):
        print(f"\nLoading model from checkpoint: {resume_path}")
        model = YOLO(resume_path)
    else:
        print("Loading YOLOv5nu model...")
        # Use pretrained model from data/models/yolov5n or download if not found
        pretrained_path = Path(__file__).parent.parent / 'data' / 'models' / 'yolov5n' / 'yolov5nu.pt'
        if pretrained_path.exists():
            model = YOLO(str(pretrained_path))
        else:
            model = YOLO('yolov5nu.pt')  # Download pretrained YOLOv5nu weights
    
    # Training configuration
    print("\nTraining Configuration:")
    print(f"  Model: yolov5nu (nano, Ultralytics optimized)")
    print(f"  Dataset: {args.data}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch}")
    print(f"  Image size: {args.imgsz}")
    print(f"  Device: {device}")
    if resume_path:
        print(f"  Resuming: Yes (from {resume_path})")
    else:
        print(f"  Resuming: No (starting fresh)")
    print()
    print("Press Ctrl+C to pause training and save checkpoint")
    print("=" * 60)
    
    # Start training
    print("\nStarting training...")
    print("=" * 60)
    
    try:
        # Prepare training arguments
        train_args = {
            'data': args.data,                    # Dataset configuration file
            'epochs': args.epochs,                # Number of training epochs
            'batch': args.batch,                  # Batch size
            'imgsz': args.imgsz,                 # Image size
            'device': device,                     # Use GPU if available, else CPU
            'project': args.project,              # Project directory
            'name': args.name,                    # Experiment name
            'patience': 50,                       # Early stopping patience
            'save': True,                         # Save checkpoints
            'save_period': 10,                   # Save checkpoint every N epochs
            'val': True,                          # Validate during training
            'plots': True,                        # Generate training plots
            'verbose': True,                      # Verbose output
        }
        
        # Add resume parameter if resuming from checkpoint
        # Note: When loading from checkpoint, Ultralytics will automatically resume
        # but we can also explicitly set resume=True to ensure proper resumption
        if resume_path and os.path.exists(resume_path):
            train_args['resume'] = True
        
        results = model.train(**train_args)
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print(f"\nBest weights saved to: {args.project}/{args.name}/weights/best.pt")
        print(f"Last weights saved to: {args.project}/{args.name}/weights/last.pt")
        print(f"\nResults directory: {args.project}/{args.name}/")
        
        if not torch.cuda.is_available():
            print("\nNote: Training used CPU (CUDA not available).")
            print("      For faster training, consider using a GPU-enabled environment.")
        
        print("\nTraining metrics and plots are available in the results directory.")
        
    except KeyboardInterrupt:
        # This should be caught by signal_handler, but just in case
        signal_handler(None, None)
    except Exception as e:
        print(f"\nError during training: {e}")
        print("\nTo resume from the last checkpoint, run:")
        latest_checkpoint = find_latest_checkpoint()
        if latest_checkpoint:
            print(f"  python train_yolov5.py --resume {latest_checkpoint}")
        else:
            print(f"  python train_yolov5.py --resume")
        raise


if __name__ == "__main__":
    main()

