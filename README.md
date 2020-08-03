# Dataclass Command-line Interface

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![image](https://codecov.io/gh/malte-soe/dataclass-cli/branch/master/graph/badge.svg)](https://codecov.io/gh/malte-soe/dataclass-cli)

# Installation
From [pip](https://pypi.org/project/dc-cli/):
```bash
pip install dc-cli
```

# Usage
```python
from dataclasses import dataclass, fields
import dataclass_cli

@dataclass_cli.add
@dataclass
class Model:
    num_layers: int
    learning_rate: float
    training: bool

model = Model()
print(model)
```
Output:
```bash
❯ python test.py --help
usage: test.py [-h] --model_num_layers MODEL_NUM_LAYERS --model_learning_rate MODEL_LEARNING_RATE (--model_training | --no-model_training)

optional arguments:
  -h, --help            show this help message and exit

model:
  --model_num_layers MODEL_NUM_LAYERS
  --model_learning_rate MODEL_LEARNING_RATE
  --model_training
  --no-model_training
❯ python test.py --model_num_layers 10 --model_learning_rate 0.1 --no-model_training
Model(num_layers=10, learning_rate=0.1, training=False)
```

# License
[MIT](LICENSE)
