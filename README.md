# StreamScale

StreamScale is a backend-focused video transcoding platform built to simulate a real-world media processing pipeline. The project allows users to upload videos, process them asynchronously into multiple resolutions using FFmpeg, track live processing progress, and download the generated outputs.

The main goal of this project was to design and implement a scalable backend architecture using modern production-oriented tools such as FastAPI, Celery, Redis, PostgreSQL, Docker, and AWS S3.

---

# Features

* Upload videos using pre-signed S3 upload URLs
* Asynchronous video transcoding with Celery workers
* Multi-resolution video generation using FFmpeg
* Real-time task progress tracking
* Download processed videos using temporary secure URLs
* Persistent job metadata storage using PostgreSQL
* Cloud storage support using AWS S3
* Dockerized backend services
* Retry handling for failed processing tasks
* Cleanup policy for old jobs and storage

---

# Tech Stack

## Backend

* FastAPI
* Python
* SQLAlchemy

## Task Queue & Processing

* Celery
* Redis
* FFmpeg

## Storage

* AWS S3
* Neon PostgreSQL

## DevOps

* Docker
* Docker Compose

---

# Architecture Overview

```text
Frontend
   ↓
FastAPI Backend
   ↓
Redis Queue (Broker + Result Backend)
   ↓
Celery Worker
   ↓
FFmpeg Processing
   ↓
AWS S3 Storage
   ↓
Neon PostgreSQL Metadata Storage
```

---

# Project Workflow

## 1. Upload Request

The client sends a request containing the original filename.

The backend:

* validates the file type
* creates a unique job ID
* stores job metadata in PostgreSQL
* generates a pre-signed S3 upload URL

The frontend uploads the video directly to S3.

---

## 2. Start Processing

Once upload is completed, the frontend triggers processing.

The backend:

* sends a transcoding task to Redis through Celery
* updates the job state in PostgreSQL

---

## 3. Video Transcoding

The Celery worker:

* downloads the uploaded file from S3
* processes it using FFmpeg
* generates multiple resolutions
* uploads processed outputs back to S3
* continuously updates progress in Redis

Generated resolutions:

* 360p
* 720p
* 1080p

---

## 4. Status Tracking

The backend checks Celery task progress using Redis.

Users can:

* view processing progress
* monitor per-resolution status
* receive download links after completion

---

## 5. Download

Processed files are downloaded using temporary pre-signed S3 URLs.

This avoids routing large files through the backend server.

---

# Environment Variables

Create environment variables by taking reference from env.example

---

# Running the Project

## Clone Repository

```bash
git clone
cd StreamScale
```

---

## Start Docker Services

```bash
docker compose up --build
```

Services started:

* FastAPI backend
* Celery worker
* Redis

---

# Database Migration

The project uses Neon PostgreSQL as the cloud database.

SQLAlchemy automatically creates required tables during application startup.

---

# Cleanup Policy

To avoid unnecessary cloud storage and database growth:

* Completed jobs are retained for 24 hours
* Failed jobs are retained for 3 days for debugging purposes
* Old S3 files and corresponding database entries are periodically removed

---

# Retry Handling

Celery retry handling is implemented for failed transcoding jobs.

Features:

* automatic retry attempts
* retry state tracking
* failure logging
* permanent failure handling after retry exhaustion

---

# Production-Oriented Design Decisions

Some backend decisions made during development:

* Direct S3 uploads instead of storing videos on the backend server
* Asynchronous processing using Celery workers
* Redis-based task queue and progress tracking
* Persistent metadata storage using PostgreSQL
* Separation of processing workers from API server
* Dockerized services for portability and deployment readiness

---

# Challenges Faced

Some challenges solved during development:

* Handling long-running FFmpeg tasks asynchronously
* Tracking transcoding progress in real time
* Managing temporary cloud storage URLs
* Designing retry handling for failed jobs
* Migrating local PostgreSQL data to Neon cloud PostgreSQL
* Coordinating Celery, Redis, PostgreSQL, and S3 together

---

# Future Improvements

Possible future enhancements:

* HLS streaming support
* User authentication
* Video thumbnails and previews
* Distributed worker scaling
* Monitoring and observability
* Kubernetes deployment
* WebSocket-based live progress updates

---

# Why This Project Was Built

This project was built primarily to strengthen backend engineering skills by working on a system that combines:

* asynchronous task processing
* cloud storage
* distributed services
* database persistence
* Dockerized infrastructure
* media processing workflows

The focus was not just on making the application work locally, but on understanding how production-style backend systems are designed and connected together.
