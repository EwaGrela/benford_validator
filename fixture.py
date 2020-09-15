import io

# Fixture for tests

# FIXME: This violates DRY principle, but one must generate the file three times, one for each test
csv_file = ("State,Town,some_data\n"
    "Alabama,Abbeville,2930\n"
    "Alabama,Adamsville,4782\n"
    "Alabama,Addison,709\n"
    "Alabama,Akron,433\n"
    "Alabama,Alabaster,29861\n"
    "Alabama,Albertville,20115\n")

csv_file = io.BytesIO(csv_file.encode("utf-8"))

csv_file2 = ("State,Town,some_data\n"
    "Alabama,Abbeville,2930\n"
    "Alabama,Adamsville,4782\n"
    "Alabama,Addison,709\n"
    "Alabama,Akron,433\n"
    "Alabama,Alabaster,29861\n"
    "Alabama,Albertville,20115\n")

csv_file2 = io.BytesIO(csv_file2.encode("utf-8"))

csv_file3 = ("State,Town,some_data\n"
    "Alabama,Abbeville,2930\n"
    "Alabama,Adamsville,4782\n"
    "Alabama,Addison,709\n"
    "Alabama,Akron,433\n"
    "Alabama,Alabaster,29861\n"
    "Alabama,Albertville,20115\n")

csv_file3 = io.BytesIO(csv_file3.encode("utf-8"))


csv_file4 = ("Country,Town,population\n"
    "Poland,Warsaw,2593000\n"
    "Poland,Poznan,178200\n"
    "Poland,Gdansk,709000\n"
    "Poland,Tychy,433000\n"
    "Poland, Krakow,1298610\n"
    "Poland,Warsaw2,1593002\n"
    "Poland,Poznan2,478202\n"
    "Poland,Gdansk2,709002\n"
    "Poland,Tychy2,433002\n"
    "Poland, Krakow2,1298612\n"
    "Alabama,Albertville3,20114\n")

csv_file4 = io.BytesIO(csv_file4.encode("utf-8"))