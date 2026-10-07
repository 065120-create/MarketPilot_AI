def generate_html_report(job_data: dict) -> str:
    """Generate an HTML report for a completed job."""
    return f"""
    <html>
        <head><title>MarketPilot Report</title></head>
        <body>
            <h1>Campaign Report</h1>
            <p>Status: {job_data.get('status')}</p>
            <h2>Results</h2>
            <pre>{job_data.get('results', {})}</pre>
        </body>
    </html>
    """

def generate_markdown_report(job_data: dict) -> str:
    """Generate a Markdown report for a completed job."""
    return f"""# Campaign Report
Status: {job_data.get('status')}

## Results
{job_data.get('results', {})}
"""
