🛡️ NariKawach
AI Guardian Network for Women’s Safety
📌 Overview

NariKawach is an AI-powered women safety system designed to identify potentially unsafe situations in real time by analyzing movement behavior, route patterns, and environmental risk factors.

The system focuses on early risk detection and intelligent intervention, enabling preventive action before a situation escalates, while ensuring user consent and control.

🎯 Problem Statement

Women frequently face safety risks during daily commutes, late-evening travel, or in isolated environments.
Most existing solutions depend on manual emergency actions or post-incident reporting, which often activate too late.

There is a need for a system that can:

Learn normal daily movement behavior

Detect abnormal or risky patterns

Assist users proactively and intelligently

Reduce dependency on panic-based responses

💡 Proposed Solution

NariKawach acts as a digital safety guardian that:

Learns a user’s normal routes, time patterns, and movement behavior

Detects route deviations, unusual timing, and low-safety environments

Calculates a dynamic risk score

Triggers context-aware safety interventions when required

The system does not predict crimes.
It identifies behavioral anomalies combined with environmental risk indicators.

🤖 AI & Detection Logic
1️⃣ Route & Behavior Analysis

The system builds a baseline using:

Daily routes

Time windows

Movement speed

Typical stop durations

A situation is flagged only when multiple deviations occur together, such as:

Route deviation

Late travel time

Low crowd density

Poor lighting

Prolonged inactivity

2️⃣ Risk Scoring Engine

Each risk factor contributes to an overall score:

Risk Score = Crime Density + Crowd Level + Lighting + Time + Route Deviation


Risk levels:

Low – Normal behavior

Medium – Unusual but non-critical

High – Potential safety concern

3️⃣ Stalking Pattern Detection

NariKawach identifies repeated proximity anomalies across multiple days.

If an unknown device repeatedly appears:

On the same route

For extended durations

Across multiple days

The probability of coincidence decreases, and the system flags a possible stalking pattern.

🔁 System Workflow
Step 1: User Registration

User installs the web application (PWA)

Adds emergency contacts

Enables location access

Step 2: Baseline Learning

Records daily routes

Learns time and movement patterns

Builds a normal behavior profile

Step 3: Real-Time Monitoring

GPS-based location tracking

Speed and route comparison

Crowd density and lighting context

Step 4: Risk Engine

Computes risk score

Categorizes risk level

Step 5: Intelligent Intervention

Low Risk: No action

Medium Risk: Suggest safer route or share live location

High Risk: Auto location sharing with guardians and emergency readiness

Step 6: Guardian Dashboard

Live location view

Alert notifications

Emergency status updates

⚙️ Tech Stack
Frontend

Next.js

Tailwind CSS

Mapbox / Google Maps API

Progressive Web App (PWA)

Backend

Node.js

Firebase / Supabase

WebSockets for realtime tracking

AI Layer

Python

FastAPI

Pandas

Scikit-learn

AI Models (PoC Level)

Route Detection: KNN / Dynamic Time Warping

Risk Prediction: Logistic Regression / Random Forest

Stalking Detection: Isolation Forest

Decision Agent: Rule-based AI

📊 Data Sources
Crime & Safety Data

Crime in India Dataset (Kaggle)

Urban Ride Safety Dataset (Mumbai & Delhi)

Open Government Crime Records (data.gov.in)

Location & Environment Data

Google Maps API

Mapbox API

Crowd density via traffic & pedestrian data

Open street light GIS datasets

👥 Team Distribution (30-Hour Hackathon)

Member 1 – Product Architect & Pitch Lead
Problem statement, user journey, architecture, ethics, PPT, pitch

Member 2 – Frontend & UX Engineer
UI, maps, live tracking, notifications, guardian sharing

Member 3 – Backend & Realtime Engineer
Authentication, APIs, realtime tracking, alerts

Member 4 – AI & ML Engineer
Route anomaly detection, risk scoring, stalking logic, decision agent

🎯 Goal

To build a digital guardian that:

Detects danger early

Reduces reaction time

Supports women through intelligent assistance

Enhances safety without panic

🏁 Conclusion

NariKawach demonstrates how AI can be applied to women’s safety through behavioral analysis, contextual risk assessment, and intelligent intervention, ensuring real-time protection with practical feasibility.
