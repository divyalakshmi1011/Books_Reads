import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "NNeZ3s1QfV9G3Kcuwnhl7w", "isbns": "9781632168146"})
print(res.json())