import os
import sys
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='create env')
    parser.add_argument('model', type=str, help='(densenet121_model|alexnet_model|PL_qnn_model|Qiskit_easy_2_qnn_model|Qiskit_easy_4_qnn_model)')
    parser.add_argument('--init_step', type=int, help='pre-train step')
    parser.add_argument('--train_epochs', type=int, help='training step')
    parser.add_argument('--q_num', type=int, default=4, help='training step')
    args = parser.parse_args()
    os.system(f"echo {args}")
    os.system(f"conda create {args}")
