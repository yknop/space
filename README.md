# 📡 Satellite image monitoring

![Version](https://img.shields.io/badge/Release-1.0.0-brightgreen)

This system constitutes a monitoring and filter for satellite simulations in order to avoid overloading the chain that the simulations go through and to remove those that have no value as well as to be a fault dimension in percentages for each possible type of disruption by a detailed dashboard at the end.

## 📚 Table of Contents

- [Overview](#🌐-overview)
- [System requirements](#🖥️-system-requirements)
- [Technologies](#🖥️-technologies)
- [Server Dependencies](#🖧-server-dependencies)
- [Usage](#📋-usage)
- [Installation](#⚙️-installation)

## 🌐 Overview

The system checks on each image the types of disturbances such as: saturation, blurring, smearing and more, and updates the database.

## 🖥️ System requirements

1. Visual Studio Code work environment.
2. Docker desktop.

## 🖥️ Technologies

- Server: Python
- DB: Mongo-DB

## 🖧 Server Dependencies

All dependencies are installed automatically when building the Dockerfile.

## 📋 Usage

To use the application, follow the steps below:

1. Add a folder containing blacksky images folders to test.
2. Fill the `.env` file according to `.env.sample` file.

## ⚙️ Installation

Build the docker image from the project location:

```sh
docker build -t satellite-image-monitoring .
```

Run the image:

```sh
docker run --name satellite-image-monitoring satellite-image-monitoring
```

Remove container:

```sh
docker rm satellite-image-monitoring
```

Remove image:

```sh
docker rmi satellite-image-monitoring
```

✅ In the collection of images in Mongo, you can view the results of the tests.
