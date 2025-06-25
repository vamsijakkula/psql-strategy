from flask import Flask, request, jsonify
from datetime import datetime
from tabulate import tabulate
import statistics
from typing import List, Dict, Any

app = Flask(__name__)

def format_timestamp(ts: str) -> str:
    """Format timestamp for display"""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts

def display_strategy_table(data: List[dict]) -> str:
    """Generate formatted table output"""
    headers = ["ID", "Parameter", "Value", "Timestamp", "Description", "Active"]
    rows = []
    
    for item in data:
        rows.append([
            item.get('id', ''),
            item.get('parameter', ''),
            f"{item.get('value', 0):.4f}",
            format_timestamp(item.get('timestamp', '')),
            item.get('description', '')[:25] + '...' if len(item.get('description', '')) > 25 else item.get('description', ''),
            '✓' if item.get('is_active', False) else '✗'
        ])
    
    return tabulate(rows, headers=headers, tablefmt="grid", stralign="left", numalign="right")

def analyze_parameters(data: List[dict]) -> dict:
    """Perform statistical analysis on the parameters"""
    if not data:
        return {}
    
    values = [item.get('value', 0) for item in data]
    active_values = [item.get('value', 0) for item in data if item.get('is_active', False)]
    
    return {
        "parameter_count": len(data),
        "active_count": sum(1 for item in data if item.get('is_active', False)),
        "value_stats": {
            "average": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "active_avg": statistics.mean(active_values) if active_values else 0
        },
        "top_parameters": sorted(data, key=lambda x: abs(x.get('value', 0)), reverse=True)[:3]
    }

@app.route('/strategy', methods=['POST'])
def strategy_analysis():
    try:
        # Get data from agent request
        request_data = request.json
        strategy_data = request_data.get('data', [])
        
        if not strategy_data:
            return jsonify({"error": "No data provided"}), 400
        
        # Generate outputs
        table_output = display_strategy_table(strategy_data)
        analysis = analyze_parameters(strategy_data)
        
        # Print to console
        print("\n" + "="*50)
        print("NEW REQUEST RECEIVED")
        print("="*50)
        print("\n=== STRATEGY PARAMETERS ===")
        print(table_output)
        print("\n=== ANALYSIS RESULTS ===")
        print(f"Parameters analyzed: {len(strategy_data)} ({analysis['active_count']} active)")
        print(f"Average value: {analysis['value_stats']['average']:.4f}")
        print(f"Minimum value: {analysis['value_stats']['min']:.4f}")
        print(f"Maximum value: {analysis['value_stats']['max']:.4f}")
        print("\nTop 3 parameters by absolute value:")
        for param in analysis['top_parameters']:
            print(f"- {param['parameter']}: {param['value']:.4f}")
        print("="*50 + "\n")
        
        # Prepare response
        response = {
            "status": "success",
            "display_output": table_output,
            "analysis": analysis,
            "summary": f"Analyzed {len(strategy_data)} parameters ({analysis['active_count']} active)"
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        return jsonify({
            "status": "error",
            "error_message": str(e)
        }), 500

if __name__ == '__main__':
    print("Starting strategy analysis service...")
    print("Waiting for POST requests at http://localhost:8080/strategy")
    print("="*50)
    app.run(host='0.0.0.0', port=8080)