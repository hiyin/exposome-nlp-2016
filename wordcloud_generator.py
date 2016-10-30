
"""
Minimal Example
===============
Generating a square wordcloud from the US constitution using default arguments.
"""

from os import path
from wordcloud import WordCloud, STOPWORDS

def draw_wordcloud(text):

    # Generate a word cloud image
    wordcloud = WordCloud().generate(text)
    stopwords=set(STOPWORDS)
    # Display the generated image:
    # the matplotlib way:
    import matplotlib.pyplot as plt
    plt.imshow(wordcloud)
    plt.axis("off")

    # lower max_font_size
    wordcloud = WordCloud(max_font_size=60, background_color="white",stopwords=stopwords).generate(text)
    plt.figure()
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()

# The pil way (if you don't have matplotlib)
#image = wordcloud.to_image()
#image.show()