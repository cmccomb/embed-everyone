import json                     # for saving and parsing json files
import matplotlib.pyplot        # for convering rgb to hex
import matplotlib.colors        # for getting pretty colors
import numpy                    # for generic operations
import os                       # for searching for json files
import pandas                   # dumping json into csv
import plotly.express           # plotly
from scholarly import scholarly # google scholar
import sentence_transformers    # embeddings
import sklearn.decomposition    # orient tsne
import sklearn.manifold         # make a tsne
import sys                      # for testing

df = pandas.DataFrame

# List of faculty names and google scholar IDs
faculty_in_department: list[tuple[str, str]] = [
    ("Farimani",            "aH52nxkAAAAJ"),
    ("Bedillion",           "UIS_G1YAAAAJ"),
    ("Bergbreiter",         "SU0c5P0AAAAJ"),
    ("Beuth",               None),
    ("Bolmin",              "YM2HSekAAAAJ"),
    ("Cagan",               "VtINcewAAAAJ"),
    ("de Boer",             "P1OWCkAAAAAJ"),
    ("Gomez",               None),
    ("Grande Gutiérrez",    "HzsuNvEAAAAJ"),
    ("Haidar",              None),
    ("Halilaj",             "Fr9Vhe4AAAAJ"),
    ("Jayan",               "NNSeBe4AAAAJ"),
    ("Johnson",             "GN5Mc3UAAAAJ"),
    ("Jones",               "xnyNe2EAAAAJ"),
    ("Kang",                "jcgAPTYAAAAJ"),
    ("Kara",                "_X2eOeQAAAAJ"),
    ("LeDuc",               "sLEB9iYAAAAJ"),
    ("Litster",             "7zUqi1sAAAAJ"),
    ("Majidi",              "1LyndUsAAAAJ"),
    ("Malen",               "U8r6ir4AAAAJ"),
    ("McComb",              "0P9w_S0AAAAJ"),
    ("McGaughey",           "HmNtygkAAAAJ"),
    ("Michalek",            "92jyX2EAAAAJ"),
    ("Narra",               "LxF27NYAAAAJ"),
    ("Ozdoganlar",          "F3UFKWMAAAAJ"),
    ("Panat",               "y1-WJhYAAAAJ"),
    ("Presto",              "4iYpwt8AAAAJ"),
    ("Quinn",               "2b0ZjdsAAAAJ"),
    ("Rabin",               "INTSXtcAAAAJ"),
    ("Shen",                "9KtTt28AAAAJ"),
    ("Shimada",             "pgcK25AAAAAJ"),
    ("Singh",               "lViJAdQAAAAJ"),
    ("Steif",               "NVHAIw4AAAAJ"),
    ("Sullivan",            "wXSgFr4AAAAJ"),
    ("Taylor",              "eDzzGUQAAAAJ"),
    ("Tucker",              "8N6uFIkAAAAJ"),
    ("Weber",               "7iFu3a4AAAAJ"),
    ("Webster-Wood",        "jW3whJYAAAAJ"),
    ("Whitefoot",           "3W2VK5sAAAAJ"),
    ("Zhang",               "dzHYBKcAAAAJ"),
    ("Zhao",                "z7tPc9IAAAAJ"),
]


# Function to save publications from Google Scholar
def save_publications_to_json(faculty: tuple[str, str]) -> list[dict[str, str]]:
    print(faculty[0])
    faculty_pubs = []
    if faculty[1]:
        author = scholarly.fill(scholarly.search_author_id(faculty[1]))
        for publication in author['publications']:
            # filled_publication = scholarly.fill(publication)
            filled_publication = publication
            faculty_pubs.append(filled_publication['bib'])
    with open(faculty[0] + '.json', 'w', encoding='utf-8') as f:
        json.dump(faculty_pubs, f, ensure_ascii=False, indent=4)
    return faculty_pubs


number_of_faculty: int = len(faculty_in_department) if len(sys.argv) == 1 else int(sys.argv[1])
for faculty_tuple in faculty_in_department[:number_of_faculty]:
    save_publications_to_json(faculty_tuple)

# Identify all the json files
path_to_json: str = './'
json_files: list[str] = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

# Dump all of the json files into a single dataframe
all_the_data: df = pandas.DataFrame()
for json_file in sorted(json_files, key=str.casefold):
    with open(os.path.join(path_to_json, json_file)) as json_file_path:
        json_dict: dict = json.load(json_file_path)
        json_as_df: pandas.DataFrame = pandas.DataFrame.from_dict(json_dict)
        json_as_df['faculty'] = json_file.replace(".json", "")
        all_the_data = pandas.concat([all_the_data, json_as_df], axis=0)

all_the_data.reset_index(inplace=True)

# Embed titles from publications
model = sentence_transformers.SentenceTransformer('all-mpnet-base-v2')
embeddings = model.encode(all_the_data['title'], show_progress_bar=True)

# Boil down teh data into a 2D plot
tsne_embeddings = sklearn.manifold.TSNE(n_components=2, random_state=42).fit_transform(embeddings)
pca_embeddings = sklearn.decomposition.PCA(n_components=2, random_state=42).fit_transform(tsne_embeddings)
all_the_data['x'] = pca_embeddings[:, 0]
all_the_data['y'] = pca_embeddings[:, 1]

# Make some pretty colors! 
colors = [matplotlib.colors.to_hex(x) for x in matplotlib.pyplot.cm.gist_rainbow(numpy.linspace(0, 1, len(json_files)))]

# Plot the embeddings
fig = plotly.express.scatter(
    all_the_data,
    x="x",
    y="y",
    hover_data=["title"],
    color="faculty",
    color_discrete_sequence=colors
)

# Make sure the axes are appropriately scaled
fig.update_xaxes(
    visible=False,
    autorange=False,
    range=[numpy.min(pca_embeddings[:, 0]) * 1.05, numpy.max(pca_embeddings[:, 0]) * 1.05]
)

fig.update_yaxes(
    visible=False,
    scaleanchor="x",
    scaleratio=1,
    range=[numpy.min(pca_embeddings[:, 1]) * 1.05, numpy.max(pca_embeddings[:, 1]) * 1.05]
)

# Reset the layout
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(y=0.5),
    plot_bgcolor="#191C1F",
)

# Remove the logo
fig.show(config=dict(displaylogo=False))

# Save the file
fig.write_html("index.html")
