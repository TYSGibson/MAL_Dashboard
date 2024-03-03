import streamlit as st 
import pandas as pd 
import plotly.express as px
import streamlit.components.v1 as com

stripe_checkout = '<a href = https://buy.stripe.com/14k3cWgSV4Qh7QIbII> Donate Here!</a>'

st.set_page_config(page_title = 'MAL Anime Dashboard',
                   page_icon = ':bar_chart:',
                   layout = 'wide' #sets the windows layout to full screen
                   )

data = pd.read_csv('./cleaned_data.csv',encoding='unicode_escape')

# Define your custom HTML code
custom_html = """
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7621745427704287"crossorigin="anonymous"></script>
<meta name="google-adsense-account" content="ca-pub-7621745427704287">
</head>
"""

# Display the custom HTML in your Streamlit app
st.components.v1.html(custom_html)

## Creating the side bar

st.sidebar.header("Filter Selection Here:")

# Assuming data is your DataFrame
anime = data['anime_type'].unique()
anime_list = list(anime)
anime_list.append('All')

anime_type = st.sidebar.multiselect(
    "Filter by show type:",
    options=anime_list,
    default=anime
)

# Check if 'All' is selected, if so, set anime_type to the full list
if 'All' in anime_type:
    anime_type = list(anime)  # Set anime_type to the full list

if 'All' not in anime_type:
    data = data.loc[data['anime_type'].isin(anime_type)]

# Main Page
st.title(':bar_chart: Welcome to My MAL Dashboard!')
st.markdown('##') # Basically breakspace in streamlit

# Constructing the important plots/info/KPIs

total_shows = data['title'].nunique()
avg_rating = round(data['rating'].mean(),2)
avg_members = int(round(data['member_count'].mean(),0))

left, center, right = st.columns(3)

with left:
    st.subheader('Total Shows:')
    st.subheader(f'{total_shows}')
    
with center:
    st.subheader('Average Rating:')
    st.subheader(f'{avg_rating}')
    
with right:
    st.subheader('Average Members:')
    st.subheader(f'{avg_members}')

st.markdown('---')

# Exploding the genre and using this dataframe for our plots to get a more accurate presentation of genre:
data['genre'] = data['genre'].apply(lambda x: [] if pd.isna(x) else [item.strip() for item in x.split(',')])
data_selection_explode = data.explode('genre')

genre_unique_no_all = data_selection_explode['genre'].unique()
genre_unique = list(genre_unique_no_all)
genre_unique.append('All')

genre_filter = st.sidebar.multiselect(
    "Filter by Genre:",
    options=genre_unique,
    default=genre_unique_no_all
)

if 'All' in genre_filter:
    genre_filter = genre_unique

if 'All' not in genre_filter:
    data_selection_explode = data_selection_explode.loc[data_selection_explode['genre'].isin(genre_filter)]


# Creating our plots
left , right = st.columns(2)

# Distribution of ratings across all anime:
fig_rating = px.histogram(data_selection_explode, x = 'rating', 
                          title = 'Rating Distribution Among Shows', 
                          color = 'genre', barmode = 'relative')
fig_rating.update_layout(plot_bgcolor = 'black', paper_bgcolor = 'black', font = dict(color = 'white'))

left.plotly_chart(fig_rating, use_container_width=True) # use_container_width = True allows the plots to not overlap very useful!

# Genre Pie Chart
genre_count = data_selection_explode.pivot_table(index = ['genre'], values = 'sypnopsis', aggfunc = 'count').reset_index()
genre_count.rename(columns = {'sypnopsis':'count'}, inplace = True)

fig_genre = px.pie(genre_count, names = 'genre', 
                          title = 'Distribution By Genre', 
                          values = 'count')
fig_genre.update_layout(plot_bgcolor = 'black', paper_bgcolor = 'black', font = dict(color = 'white'))


# Simple Dataframe showing the top 10 rated anime with progress bar:
data['genre'] = data['genre'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')

top_rated = data.sort_values('rating', ascending = False).head(100)

with right:
    st.markdown('Top 100     Rated Anime')
    st.dataframe(top_rated,
        column_order=("title","genre" ,"rating"),
        hide_index=True,
        width=800,
        column_config={
        "title": st.column_config.TextColumn(
            "Title",
        ),
        "genre":st.column_config.TextColumn(
            "Genre",
        ),
        "rating": st.column_config.ProgressColumn(
            "Rating",
            format="%f",
            min_value=0,
            max_value=max(top_rated['rating']),
            )}
        )
st.markdown('##')

left, right = st.columns(2)
left.plotly_chart(fig_genre, use_container_width=True)

# # Number of anime trend chart by year:
# trend = data_selection_explode.pivot_table(index = ['year_released'], values = 'sypnopsis', aggfunc = 'count').reset_index()
# trend.rename(columns = {'sypnopsis':'count'}, inplace = True)

# fig_trend = px.line(trend, x = 'year_released', y = 'count', markers = True, title = 'Number of Anime Released Over the Years')
# fig_trend.update_xaxes(range=[1930,2024])
# fig_trend.update_layout(plot_bgcolor = 'black', paper_bgcolor = 'black', font = dict(color = 'white'))

# st.plotly_chart(fig_trend,use_container_width=True)

# Member count by genre:
member = data_selection_explode.pivot_table(index = ['genre'], values = 'member_count', aggfunc = 'sum').reset_index().sort_values('member_count', ascending = False)

fig_member = px.bar(member, x = 'genre', y = 'member_count', title = 'Members by Genre', color = 'genre')
fig_member.update_layout(plot_bgcolor = 'black', paper_bgcolor = 'black', font = dict(color = 'white'))

right.plotly_chart(fig_member, use_container_width=True)

# Number of anime trend by year by genre:
trend_genre = data_selection_explode.pivot_table(index = ['year_released', 'genre'], values = 'sypnopsis', aggfunc = 'count').reset_index()
trend_genre.rename(columns = {'sypnopsis':'count'}, inplace = True)

fig_trend_genre = px.line(trend_genre, x = 'year_released', y = 'count', color = 'genre',
                    markers = True, title = 'Number of Anime Released Over the Years')
fig_trend_genre.update_xaxes(range=[1930,2024])
fig_trend_genre.update_layout(plot_bgcolor = 'black', paper_bgcolor = 'black', font = dict(color = 'white'))

st.plotly_chart(fig_trend_genre,use_container_width=True)

# Styling the Webapp

hide_st_style = '''
                <style>
                #MainMenu {visibility:hidden;}
                footer {visibility:hidden;}
                header{visibility:hidden;}
                </style>
'''

st.markdown(hide_st_style, unsafe_allow_html = True)

st.subheader('Enjoyed the work? Consider buying a cup of coffee to support me! 🥰')
st.markdown(stripe_checkout, unsafe_allow_html = True)


