"""Utiliy/Storage file for report generation"""

HTML_STYLE = """<style>
.heading-background {
background-color: #333333;
display: flex;
align-items: center;
justify-content: center;
text-align: center;
}
.heading {
color: #7fc37e;
font-size: 8;
margin: 0;
padding: 2 0 0 0
}
p {
    text-align: Center;
    color : #333333;
    font-size: 6;
    }
.container {
    grid-template-columns: repeat(2, 1fr); 
    grid-gap: 10px;
    color: white;
}
.plotly-graph-div {
display: flex;
flex-wrap: wrap;
flex-align: center;
justify-content: center;
   width: 260;
   height: 200;
}
</style>"""

REPORT_HTML = '''
    <html>
    <head>
        {style}
        <title>Daily Report</title>
    </head>
    <body>
        <div class="heading-background">
            <h1 class="heading">Daily Report</h1>
        </div>
        <div>
        <p class="intro"> {print_line}</p>
        </div>
        <div class="container">
        <table>
        <tr>
            <td>{gender_graph}</td>
            <td>{age_graph}</td>
        </tr>
        <tr>
            <td>{hrt_graph}</td>
            <td>{power_graph}</td>
        </tr>
        </table>
        </div>
        <img src="{file_path}/deloton.png">
    </body>
    '''