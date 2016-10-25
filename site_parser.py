import pandas

data = pandas.read_csv('/Users/dyin/Desktop/common_sql.csv', header=0)

chemicals = data["Chemical name"].tolist()


# chemicals = list(data.C)
# chemicals = data["Chemical name"].tolist()




