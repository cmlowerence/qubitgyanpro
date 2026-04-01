# qubitgyanpro\scripts\train_model.py

from services.ml_dataset import build_training_dataset
from services.ml_model import train_model


def run():
    dataset = build_training_dataset()

    if dataset is None:
        print("No data available")
        return

    X, y = dataset

    train_model(X, y)

    print("Model trained successfully")


if __name__ == "__main__":
    run()