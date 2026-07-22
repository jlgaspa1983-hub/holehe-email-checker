#!/usr/bin/env python3
"""
Flask web app for Random Joke Generator
Provides a REST API and web interface for jokes
"""

from flask import Flask, jsonify, render_template_string, request, send_from_directory
import asyncio
import json
from joke_generator import JokeGenerator, Joke
import os

app = Flask(__name__)

# HTML Template for web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random Joke Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        button {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-secondary {
            background: #764ba2;
            color: white;
        }
        
        select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            flex: 1;
        }
        
        .joke-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .joke-text {
            font-size: 1.1em;
            color: #333;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        
        .joke-meta {
            font-size: 0.9em;
            color: #999;
            display: flex;
            justify-content: space-between;
        }
        
        .loading {
            text-align: center;
            color: #666;
        }
        
        .error {
            color: #e74c3c;
            padding: 10px;
            background: #fadbd8;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .success {
            color: #27ae60;
            padding: 10px;
            background: #d5f4e6;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>😂 Joke Generator</h1>
        <p class="subtitle">Get random jokes from multiple sources</p>
        
        <div class="controls">
            <button class="btn-primary" onclick="getRandomJoke()">🎲 Random Joke</button>
            <button class="btn-secondary" onclick="getAllSources()">🌍 All Sources</button>
        </div>
        
        <div class="controls">
            <select id="category">
                <option value="Any">Any Category</option>
                <option value="Programming">Programming</option>
                <option value="Knock-Knock">Knock-Knock</option>
                <option value="General">General</option>
                <option value="Pun">Pun</option>
            </select>
            <button class="btn-primary" onclick="getJokeByCategory()">Get Category Joke</button>
        </div>
        
        <div id="message"></div>
        <div id="joke-container"></div>
    </div>
    
    <script>
        async function getRandomJoke() {
            showLoading();
            try {
                const response = await fetch('/api/random');
                const data = await response.json();
                
                if (response.ok) {
                    displayJoke(data);
                } else {
                    showError(data.error || 'Failed to fetch joke');
                }
            } catch (error) {
                showError('Error: ' + error.message);
            }
        }
        
        async function getJokeByCategory() {
            const category = document.getElementById('category').value;
            showLoading();
            try {
                const response = await fetch(`/api/category/${category}`);
                const data = await response.json();
                
                if (response.ok) {
                    if (data.jokes && data.jokes.length > 0) {
                        displayJoke(data.jokes[0]);
                    } else {
                        showError('No jokes found for this category');
                    }
                } else {
                    showError(data.error || 'Failed to fetch joke');
                }
            } catch (error) {
                showError('Error: ' + error.message);
            }
        }
        
        async function getAllSources() {
            showLoading();
            try {
                const response = await fetch('/api/all-sources');
                const data = await response.json();
                
                if (response.ok) {
                    displayAllSources(data);
                } else {
                    showError(data.error || 'Failed to fetch jokes');
                }
            } catch (error) {
                showError('Error: ' + error.message);
            }
        }
        
        function displayJoke(joke) {
            const container = document.getElementById('joke-container');
            container.innerHTML = `
                <div class="joke-box">
                    <div class="joke-text">${escapeHtml(joke.text)}</div>
                    <div class="joke-meta">
                        <span>📝 ${joke.source}</span>
                        <span>${joke.category ? '📂 ' + joke.category : ''}</span>
                    </div>
                </div>
            `;
            clearMessage();
        }
        
        function displayAllSources(data) {
            const container = document.getElementById('joke-container');
            let html = '';
            
            for (const [source, joke] of Object.entries(data)) {
                if (joke) {
                    html += `
                        <div class="joke-box">
                            <div style="font-size: 0.9em; color: #667eea; margin-bottom: 10px;">✓ ${source}</div>
                            <div class="joke-text">${escapeHtml(joke.text.substring(0, 150))}...</div>
                        </div>
                    `;
                } else {
                    html += `
                        <div class="joke-box" style="border-left-color: #ddd; opacity: 0.6;">
                            <div style="color: #999;">✗ ${source}: Failed to load</div>
                        </div>
                    `;
                }
            }
            
            container.innerHTML = html;
            clearMessage();
        }
        
        function showLoading() {
            document.getElementById('joke-container').innerHTML = '<div class="loading">⏳ Loading...</div>';
        }
        
        function showError(message) {
            document.getElementById('message').innerHTML = `<div class="error">❌ ${message}</div>`;
            document.getElementById('joke-container').innerHTML = '';
        }
        
        function clearMessage() {
            document.getElementById('message').innerHTML = '';
        }
        
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
        
        // Load random joke on page load
        window.onload = getRandomJoke;
    </script>
</body>
</html>
"""


def run_async(coro):
    """Run async function in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.route('/')
def index():
    """Serve web interface"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/random', methods=['GET'])
def get_random_joke():
    """Get random joke from any source"""
    try:
        joke = run_async(fetch_random_joke())
        
        if joke:
            return jsonify(joke.to_dict()), 200
        else:
            return jsonify({"error": "Failed to fetch joke"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/category/<category>', methods=['GET'])
def get_jokes_by_category(category):
    """Get jokes by category"""
    try:
        count = request.args.get('count', default=1, type=int)
        jokes = run_async(fetch_jokes_by_category(category, count))
        
        if jokes:
            return jsonify({"jokes": [j.to_dict() for j in jokes]}), 200
        else:
            return jsonify({"error": "No jokes found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/all-sources', methods=['GET'])
def get_all_sources():
    """Get jokes from all sources"""
    try:
        jokes_dict = run_async(fetch_all_sources())
        
        result = {}
        for source, joke in jokes_dict.items():
            result[source] = joke.to_dict() if joke else None
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "Joke Generator API"}), 200


# Async helper functions
async def fetch_random_joke():
    """Fetch random joke"""
    async with JokeGenerator() as gen:
        return await gen.get_random_joke()


async def fetch_jokes_by_category(category, count):
    """Fetch jokes by category"""
    async with JokeGenerator() as gen:
        return await gen.get_jokes_by_category(category, count)


async def fetch_all_sources():
    """Fetch from all sources"""
    async with JokeGenerator() as gen:
        return await gen.get_all_sources()


if __name__ == '__main__':
    print("🎲 Starting Joke Generator API...")
    print("📍 Navigate to http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)
