# Next-Generation AI Agents for Investment Strategy and Risk Governance

An AI-powered investment analytics and portfolio governance platform developed using Python, MongoDB, Flask, Plotly, and Machine Learning techniques.

The system combines multiple AI agents for market analysis, sentiment evaluation, technical strategy analysis, portfolio optimization, risk governance, and backtesting to generate intelligent BUY / HOLD / SELL investment decisions through a modern fintech-style dashboard.

---

# Project Overview

This project simulates an AI-driven investment decision platform that integrates:

* Fundamental Analysis
* News Sentiment Analysis
* Technical Strategy Evaluation
* Risk Management
* Portfolio Construction
* Backtesting
* Analytics & Visualization

The platform processes financial market data, generates AI-based investment signals, evaluates portfolio performance, and visualizes results through an interactive dashboard.

---

# Technology Stack

## Backend

* Python
* Flask
* MongoDB

## Data & Analytics

* Pandas
* NumPy
* yfinance
* VADER Sentiment Analysis
* Google News RSS

## Visualization

* Plotly
* TailwindCSS
* HTML/CSS/JavaScript

---

# System Architecture

Market Data Collection
        ↓
Fundamental Analysis
        ↓
News Sentiment Analysis
        ↓
Agentic AI Governance System
        ↓
Portfolio Construction Engine
        ↓
Backtesting Engine
        ↓
Analytics Engine
        ↓
Interactive Dashboard

---

# AI Agents

## Fundamentals Agent

Analyzes company fundamentals and generates investment signals based on financial strength.

## Sentiment Agent

Uses Google News RSS and VADER sentiment analysis to evaluate market sentiment.

## Strategy Agent

Implements SMA 50 / SMA 200 crossover strategy for technical signal generation.

## Risk Agent

Calculates volatility, detects conflicts between agents, and applies risk governance rules.

## Governance Agent

Combines all AI agent outputs into a weighted composite score to generate final BUY / HOLD / SELL decisions.

---

# Composite Decision Logic

Composite Score Formula:

* Fundamentals Agent → 40%
* Sentiment Agent → 20%
* Strategy Agent → 40%

Final Decision Rules:

* BUY → Score ≥ 60
* HOLD → Score between 40 and 60
* SELL → Score < 40

---

# Key Features

* Multi-Agent AI Investment System
* Portfolio Allocation Engine
* Risk Governance Framework
* Historical Backtesting
* Sharpe Ratio Calculation
* Alpha Calculation
* Maximum Drawdown Analysis
* Interactive Fintech Dashboard
* Real-time Style Auto Refresh
* MongoDB Data Pipeline
* AI Explainability System

---

# Dashboard Features

## Portfolio Analytics

* Portfolio Return
* Benchmark Return
* Alpha
* Sharpe Ratio
* Maximum Drawdown

## Portfolio Visualization

* Portfolio Allocation Donut Chart
* Equity Curve
* Benchmark Comparison
* Cumulative Return Charts

## AI Insights

* AI Decision Distribution
* Composite Scores
* AI Confidence Scores
* BUY / HOLD / SELL Recommendation Cards

## Risk Analytics

* Drawdown Charts
* Volatility Monitoring
* Risk Flag Detection

## Real-Time Style Features

* Live Market Ticker
* Auto Refresh Dashboard
* Dynamic KPI Cards
* Interactive Charts

---

# Project Structure

```bash
Major Project/
│
├── agentic_ai/
│   ├── analytics/
│   ├── backtesting/
│   ├── governance/
│   ├── portfolio/
│   ├── risk/
│   ├── signals/
│   ├── config.py
│   └── pipeline.py
│
├── dashboard/
│   ├── templates/
│   └── server.py
│
├── database/
├── data_collection/
├── fundamental_analysis/
├── config/
│
├── main.py
├── refresh_data.py
└── test_mongo.py
```

---

# Backtesting Metrics

The system evaluates strategy performance using:

* Portfolio Return
* Benchmark Return
* Alpha
* Sharpe Ratio
* Maximum Drawdown
* Equity Curve Analysis

---

# Dashboard UI

The dashboard is designed with a modern fintech-inspired interface featuring:

* Dark Neon Theme
* Glassmorphism Design
* Interactive Plotly Visualizations
* Dynamic AI Recommendation Cards
* Portfolio Heatmaps
* Animated Charts
* Live Market Ticker

---

# Future Enhancements

* Reinforcement Learning Portfolio Optimization
* Real-Time Market Streaming
* Cloud Deployment
* Advanced Risk Analytics
* 3D Financial Visualizations
* LLM-Based Financial Reasoning
* AI Chat Assistant for Portfolio Insights

---

# Installation

## Clone Repository

```bash
git clone https://github.com/Karthik-0027/Next-Generation-AI-Agents-for-Investment-Strategy-and-Risk-Governance.git
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Project

```bash
python main.py
```

## Launch Dashboard

```bash
python dashboard/server.py
```

---

# Author

Karthik Gollapudi
B.Tech – Data Science
Bapatla Engineering College

---

# Project Status

Completed and fully functional end-to-end AI investment analytics pipeline with interactive dashboard and portfolio governance system.
