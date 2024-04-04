# -*- coding: utf-8 -*-
"""M23CSA019_DLOps_ClassAssignment_2_Q_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PwSgRd8JL5m8SdZta2-pbF6_9OeM_6V7
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, datasets, transforms
import matplotlib.pyplot as plt

# Step 1: Load pre-trained ResNet50 model
model = models.resnet50(pretrained=True)

# Step 2: Freeze all convolutional layers
for param in model.parameters():
    param.requires_grad = False

# Step 3: Replace the last fully connected layer
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 10)  # STL10 has 10 classes

# Step 4: Prepare STL10 dataset
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to fit model input size
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])

#I am adding some extra comment in the version1 for the model existed in main already

train_set = datasets.STL10(root='./data', split='train', download=True, transform=transform)
test_set = datasets.STL10(root='./data', split='test', download=True, transform=transform)

train_loader = torch.utils.data.DataLoader(train_set, batch_size=32, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_set, batch_size=32, shuffle=False)

# Configuration-specific model modifications
def modify_model(config_name, model_config):
    model = model_config['model'](pretrained=True)
    for param in model.parameters():
        param.requires_grad = False

    if config_name == 'ResNet50_Dropout':
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_ftrs, 10)  # STL10 has 10 classes
        )
    else:  # Applies to both ResNet18 and ResNet50_LR_Adjusted
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, 10)  # STL10 has 10 classes
    
    return model

# Training loop
def train_model(model, optimizer, criterion, num_epochs=5):
    model.train()
    train_losses = []

    for epoch in range(num_epochs):
        running_loss = 0.0
        correct = 0
        total = 0

        for inputs, labels in train_loader:
            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / len(train_loader)
        epoch_accuracy = correct / total
        train_losses.append(epoch_loss)

        print(f'Epoch {epoch+1}, Loss: {epoch_loss}, Accuracy: {epoch_accuracy}')

    return train_losses

# Configurations
configurations = {
    'ResNet18': {
        'model': models.resnet18,
        'lr': 0.001
    },
    'ResNet50_Dropout': {
        'model': models.resnet50,
        'lr': 0.001  # Adjust as needed
    },
    'ResNet50_LR_Adjusted': {
        'model': models.resnet50,
        'lr': 0.0001
    }
}

# Train and evaluate each configuration
results = {}
for config_name, config in configurations.items():
    print(f"\nTraining configuration: {config_name}")
    model = modify_model(config_name, config)
    optimizer = optim.Adam(model.fc.parameters(), lr=config['lr'])
    criterion = nn.CrossEntropyLoss()
    train_losses = train_model(model, optimizer, criterion, num_epochs=5)  # Adjust num_epochs as needed
    results[config_name] = train_losses

# Plot training curves
plt.figure(figsize=(10, 5))
for config_name, train_losses in results.items():
    plt.plot(range(1, len(train_losses) + 1), train_losses, label=f'{config_name} Loss')

plt.xlabel('Epochs')
plt.ylabel('Training Loss')
plt.title('Training Loss Curves')
plt.legend()
plt.show()