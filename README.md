🛡️ NariKawach
Your Silent Safety Companion

NariKawach is a privacy-first, consent-driven women’s safety platform designed to support users during travel through real-time situational awareness, trusted guardian readiness, and calm emergency escalation — without intrusive surveillance or background tracking.

This repository contains the complete frontend, backend, and AI-ready architecture used for the hackathon submission, built with production-grade engineering practices and ethical UX principles.

🌍 Problem Statement

Most existing safety applications rely on:

Continuous background tracking

Panic-driven interfaces

Invasive data collection

These approaches often reduce trust and discourage long-term usage.

NariKawach solves this by design.

🌟 Core Principles

Consent First – Monitoring begins only when the user starts a trip

Calm Over Panic – Informative, reassuring UI instead of fear-based alerts

Privacy by Default – No passive tracking, no silent data sharing

✨ Key Features
🔐 Secure Authentication

Email-based login and signup

Backend-managed authentication

Protected routes with defensive rendering

Frontend independent of auth SDKs

👥 Guardian Management

Add and manage trusted emergency contacts

Secure backend APIs for guardian operations

Guardians ready for escalation scenarios

🧭 Trip-Based Safety Monitoring

Safety tracking activates only during user-initiated trips

Clear trip lifecycle: start → monitor → end

No background or passive tracking

🗺️ Live Location Map

Real-time location via Browser Geolocation API

Interactive map using Leaflet + OpenStreetMap

Graceful fallbacks to ensure demo reliability

Location visible only during active trips

⚠️ Risk-Level Awareness

Clear safety states: Low · Medium · High

UI-based escalation indicators

Designed to inform without inducing panic

🚨 Emergency Mode

Dedicated emergency screen

Displays guardian contacts and live location

Intentional, confirmation-based escalation flow

🧪 Demo Mode (Developer-Friendly)

Manual risk simulation (Medium / High)

Emergency flow testing without real danger

Ideal for hackathons and live demos

🔒 Privacy by Design

Location data used only during active trips

No background surveillance

No data sharing without explicit consent

🧰 Technology Stack
Frontend

React + TypeScript

Vite (Build Tool)

Tailwind CSS + shadcn/ui

React Router DOM

TanStack React Query

React Hook Form + Zod

Leaflet (OpenStreetMap tiles)

Backend

Node.js + Express

Supabase (Auth, Database, RLS)

REST-based API architecture

WebSocket-ready for real-time extensions

AI / ML Layer

FastAPI-based microservice

Containerized using Docker

Independently deployable and scalable

Accepts trip context and returns:

Risk score

Risk level

Confidence

Explanation

⚠️ The AI service is optional for core functionality and designed for future expansion.

🗄️ Database Overview

The system uses a minimal, secure schema protected with Row Level Security (RLS):

Table	Purpose
guardians	Trusted emergency contacts
trips	Trip lifecycle and outcomes
risk_status	Current safety state

Each user can only read and write their own data.

🧭 Application Routes
Route	Description
/	Landing & trust overview
/auth	Login / Signup
/onboarding	Guardian setup & consent
/home	Dashboard & trip controls
/emergency	Emergency escalation
/history	Past trip log
/settings	Guardians & safety toggles
/preferences	Sensitivity & alert settings
/help	Transparency & help
*	404 fallback
🚀 Running the Project Locally
Prerequisites

Node.js v18+

npm

(Optional) Docker — only for ML service

Setup
# Install dependencies
npm install

# Start development server
npm run dev


The app will be available at:

http://localhost:8081


Docker is not required for authentication, map, or demo flows.

🔐 Environment Variables

Create a .env file (never commit it):

VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

🧪 Demo Mode

To ensure safe and reliable hackathon demonstrations, NariKawach includes a Demo Mode:

Simulate Medium / High risk levels

Trigger emergency workflows manually

No real danger or alerts

Designed for judges and live demos

📱 Responsive Design

Mobile-first layout

Touch-friendly controls

Fixed bottom navigation

Calm animations and soft color palette

🧠 Architecture Highlights

Backend-owned authentication

API-first data flow

Defensive UI rendering (no white screens)

Clear separation of concerns:

Frontend → UX & state

Backend → auth, data, orchestration

AI service → risk evaluation

🛣️ Planned Enhancements (Post-Hackathon)

These features were intentionally scoped out to ensure stability and ethical deployment:

SMS / WhatsApp alerts to guardians

AI-driven real-time risk detection

Hardware-based panic triggers

Route playback & historical maps

Production-grade notification services

👥 Authors & Contributors

This project was collaboratively designed, developed, and integrated by:

Vansh Jain
Frontend Architecture, UX Flow, System Integration & Final Stabilization

Ansh Soni
Backend Development, API Design & Database Integration

Meet Vyas
Machine Learning Service Architecture & Risk Logic

Prince Koladiya
AI/ML Integration Support & System Testing

Developed as a collaborative hackathon submission with clear ownership across frontend, backend, and AI systems.
