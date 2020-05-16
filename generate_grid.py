from PIL import Image

from PIL import Image
import requests
from io import BytesIO

new_im = Image.new('RGB', (400,400), "WHITE")

count = 0

users = [
    'airbnb',
    'apple',
    'dropbox',
    'facebook',
    'github',
    'heroku',
    'google',
    'grab',
    'instacart',
    'lyft',
    'medium',
    'pinterest',
    'shopify',
    'skyscanner',
    'slackhq',
    'soundcloud',
    'spotify',
    'StackExchange',
    'stripe',
    'tinder',
    'trello',
    'uber',
    'yahoo',
    'yelp',
    'zomato'
]


for i in range(0,500,100):
    for j in range(0,500,100):
        url = "https://github.com/{}.png".format(users[count])
        response = requests.get(url)
        im = Image.open(BytesIO(response.content))
        im.thumbnail((100,100), Image.ANTIALIAS)
        new_im.paste(im, (i,j))
        count += 1
new_im.show()
