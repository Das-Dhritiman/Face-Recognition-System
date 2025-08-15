import argparse
from src.data_collection import collect_data
from src.model_training import train_model
from src.expression_recognition import recognize_expressions

def main():
    """
    Main function to parse command-line arguments and run the selected mode.
    """
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Facial Expression Recognition Program")
    parser.add_argument(
        "--mode", 
        type=str, 
        required=True, 
        choices=['collect', 'train', 'recognize'],
        help="The mode to run the program in: 'collect' to gather data, 'train' to build the model, or 'recognize' to perform real-time recognition."
    )
    parser.add_argument(
        "--expression", 
        type=str, 
        help="Required for 'collect' mode. The name of the expression you are recording (e.g., 'smiling', 'crying')."
    )

    args = parser.parse_args()

    # Execute the corresponding function based on the mode
    if args.mode == 'collect':
        if not args.expression:
            # The --expression argument is mandatory for collect mode
            parser.error("--expression is required when using --mode collect")
        else:
            collect_data(args.expression)
    
    elif args.mode == 'train':
        train_model()
    
    elif args.mode == 'recognize':
        recognize_expressions()

if __name__ == "__main__":
    # This ensures the main function is called only when the script is executed directly
    main()

