
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Veri yükle
df = pd.read_excel("AI_Rapor.xlsx", sheet_name="Sayfa1")

# Alanlar
alanlar = [
    'Okuma Becerileri', 
    'Fen Okuryazarlığı', 
    'Matematik Okuryazarlığı', 
    'Problem Çözme Becerileri', 
    'Finansal Okuryazarlık'
]

# Mapping
mapping = {0: 'Temel Altı', 1: 'Temel', 2: 'Orta', 3: 'Üst', 4: 'İleri'}
colors = {
    'Temel Altı': '#87CEEB',
    'Temel': '#1E4B9E',
    'Orta': '#F7951D',
    'Üst': '#7F3F98',
    'İleri': '#E6007E'
}

# Layout
app.layout = html.Div([
    html.H1("BEDEP 5. Sınıf Yeterlik Düzeyleri", style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='alan-dropdown',
            options=[{'label': i, 'value': i} for i in alanlar],
            value='Okuma Becerileri',
            style={'width': '48%', 'display': 'inline-block'}
        ),
        dcc.Dropdown(
            id='okul-dropdown',
            options=[{'label': okul, 'value': okul} for okul in df['Okul'].unique()],
            placeholder="Okul Seçiniz",
            style={'width': '48%', 'display': 'inline-block', 'float': 'right'}
        )
    ], style={'padding': '10px'}),

    html.Div(id='grafikler', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'})
])

# Fonksiyonlar
def create_percentage_bar(data, title, guide_lines=None):
    fig = go.Figure()
    for level in ['Temel Altı', 'Temel', 'Orta', 'Üst', 'İleri']:
        fig.add_trace(go.Bar(
            name=level,
            x=[title],
            y=[(data == level).sum() / len(data) * 100],
            marker_color=colors[level],
            width=[0.5]
        ))
    fig.update_layout(
        barmode='stack',
        barnorm='percent',
        title=title,
        plot_bgcolor='white',
        yaxis=dict(title="%", range=[0, 100], showgrid=True, gridcolor='lightgrey'),
        xaxis=dict(showgrid=False)
    )
    if guide_lines:
        for y in guide_lines:
            fig.add_shape(
                type="line",
                x0=-0.5,
                x1=0.5,
                y0=y,
                y1=y,
                line=dict(color="red", width=2, dash="dash")
            )
    return fig

# Callbacks
@app.callback(
    Output('grafikler', 'children'),
    Input('alan-dropdown', 'value'),
    Input('okul-dropdown', 'value')
)
def update_graph(alan, okul):
    genel_data = df[alan].map(mapping)
    guide_points = []
    sorted_values = (genel_data.value_counts(normalize=True).sort_index().cumsum() * 100)
    for i in range(1, 5):
        guide_points.append(sorted_values.iloc[i-1])

    genel_graph = dcc.Graph(figure=create_percentage_bar(genel_data, "Genel", guide_points))

    graphs = [genel_graph]

    if okul:
        okul_data = df[df['Okul'] == okul]
        okul_graph = dcc.Graph(figure=create_percentage_bar(okul_data[alan].map(mapping), okul, guide_points))

        graphs.append(okul_graph)

        for sube in okul_data['Şube'].unique():
            sube_data = okul_data[okul_data['Şube'] == sube]
            sube_graph = dcc.Graph(figure=create_percentage_bar(sube_data[alan].map(mapping), sube, guide_points))
            graphs.append(sube_graph)

    return graphs

if __name__ == "__main__":
    app.run_server()
