from app.scrapers.farfetch import main as farfetch_main
from app.scrapers.flannels import main as flannels_main
from app.scrapers.nanushka import main as nanushka_main
from app.scrapers.moda_operandi import main as moda_main

def run_all():
    print("Starting Farfetch scraping...")
    farfetch_main(reset_qdrant=False)

    print("Starting Flannels scraping...")
    flannels_main(reset_qdrant=False)

    print("Starting Nanushka scraping...")
    nanushka_main(reset_qdrant=False)

    print("Starting Moda Operandi scraping...")
    moda_main(reset_qdrant=False)

if __name__ == "__main__":
    run_all()
