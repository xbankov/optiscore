def select_album(google_photos):
    albums = google_photos.albums().list().execute()["albums"]
    for i, album in enumerate(albums):
        print(f"ID {i}: {album['title']}")

    while True:
        number = input("Enter ID of the album to process: ")
        if number.isdigit():
            number = int(number)
            if 0 <= number < len(albums):
                break
            else:
                print(f"Input is not in a correct range: {number}")
        else:
            print(f"Input is not a digit: {number}")
    return albums[number]
