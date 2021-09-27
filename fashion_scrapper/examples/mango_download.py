from multiprocessing import Pool, freeze_support
from pathlib import Path

from selenium.common.exceptions import TimeoutException

from scrapper.brand.mango.Mango import Mango
from scrapper.brand.mango.consts.parser import *
from scrapper.brand.mango.helper.download.DownloadHelper import DownloadHelper
from scrapper.util.io import Json_DB
from scrapper.util.list import includes_excludes_filter, flatten
from scrapper.util.web.dynamic import driver as d_driver
from tqdm.auto import tqdm

def download_category(category, mango, sub_categories):
    path = Path(BASE_PATH, category["name"])
    path.mkdir(parents=True, exist_ok=True)

    dl_settings = {
        "visited_db": Json_DB(BASE_PATH, "visited_new.json"),
        "logger": logger,
        "brand_api": mango,
        "category_path": path
    }

    dl_helper = DownloadHelper(**dl_settings)

    categories_filterd = [x for x in sub_categories if includes_excludes_filter(x, includes=category["includes"],
                                                                       excludes=category["excludes"])]
    logger.debug(f"Categories: {len(categories_filterd)} | {categories_filterd}")

    responses = [dl_helper.download_images(x, IGNORE_CATEGORY_EXISTING=FORCE_RESCAN) \
                for x in tqdm(categories_filterd, desc="Download Category")]

    return responses

def download_category_(category, mango, sub_categories):
    return download_category(category, mango=mango, sub_categories=sub_categories)
#    try:
#        return download_category(category, mango=mango, sub_categories=sub_categories)
#    except TimeoutException as e:
#        return [[{"category": category, "exception": e}]]

def cat_dl_fn(info):
    category, sub_categories = info
    with d_driver() as driver:
        mango = Mango(driver=driver, logger=logger)
        return download_category_(category, mango=mango, sub_categories=sub_categories)
if __name__ == "__main__":
    responses = []
    freeze_support()
    sub_categories = None
    with d_driver() as driver:
        mango = Mango(driver=driver, logger=logger)
        sub_categories = mango.list_categories("https://shop.mango.com/de/herren")
    assert sub_categories
    with Pool(THREADS) as p:
        jobs = zip(CATEGORIES, [sub_categories] * len(CATEGORIES))
        r = p.map(cat_dl_fn, tqdm(jobs, desc=f"i) Download Cat. {THREADS} Threads", total=len(CATEGORIES)))
        #r = [f(x) for x in tqdm(CATEGORIES, desc=f"i) Download Cat. {THREADS} Threads", total=len(CATEGORIES))]
        r = flatten(r)
        responses.append(r)

    for cat_response in responses:
        for response in cat_response:
            try:
                if (response["num_exceptions"]) > 0:
                    print(response)
                    print("-" * 16)
            except:
                print("e"*16)
                print(response)
                print("-" * 16)



#with d_driver() as driver:
#    mango = Mango(driver=driver, logger=logger)
#    sub_categories = ['https://shop.mango.com/de/damen/beauty_c34863357', 'https://shop.mango.com/de/damen/bikinis-und-badeanzuge_c10711278', 'https://shop.mango.com/de/damen/edits/family-portraits', 'https://shop.mango.com/de/damen/edits/sneakers', 'https://shop.mango.com/de/damen/geldborsen-und-brieftaschen_c13680885', 'https://shop.mango.com/de/damen/gurtel_c13182505', 'https://shop.mango.com/de/damen/hemdblusen_c78920337', 'https://shop.mango.com/de/damen/highlights/accessories-edition_d12759120', 'https://shop.mango.com/de/damen/highlights/best-sellers_d20382381', 'https://shop.mango.com/de/damen/highlights/buro-looks_d11977841', 'https://shop.mango.com/de/damen/highlights/checkers-game_d21034350', 'https://shop.mango.com/de/damen/highlights/comfy-collection_d68477392', 'https://shop.mango.com/de/damen/highlights/denim-collection_d12098323', 'https://shop.mango.com/de/damen/highlights/denim_d11224484', 'https://shop.mango.com/de/damen/highlights/effortless_d13733388', 'https://shop.mango.com/de/damen/highlights/essential-prices_d13453711', 'https://shop.mango.com/de/damen/highlights/exklusiv-online_d19236523', 'https://shop.mango.com/de/damen/highlights/key-trends_d21332319', 'https://shop.mango.com/de/damen/highlights/neu_d18713172', 'https://shop.mango.com/de/damen/highlights/new-teen_d18713172', 'https://shop.mango.com/de/damen/highlights/plus-großen_d18947337', 'https://shop.mango.com/de/damen/highlights/promotion_d18796141', 'https://shop.mango.com/de/damen/highlights/sneakers-kollektion_d17210055', 'https://shop.mango.com/de/damen/highlights/sport-collection_d18855885', 'https://shop.mango.com/de/damen/highlights/total-look_d73805904', 'https://shop.mango.com/de/damen/highlights/umstandsmode_d11068310', 'https://shop.mango.com/de/damen/highlights/urban-essentials_d86558571', 'https://shop.mango.com/de/damen/highlights/weddings-parties_d88612206', 'https://shop.mango.com/de/damen/highlights/white-summer_d11200806', 'https://shop.mango.com/de/damen/hosen_c52748027', 'https://shop.mango.com/de/damen/jacken-und-blazer_c14845233', 'https://shop.mango.com/de/damen/jeans_c12563337', 'https://shop.mango.com/de/damen/kleider-und-overalls_c20249297', 'https://shop.mango.com/de/damen/mantel_c67886633', 'https://shop.mango.com/de/damen/masken_c11122295', 'https://shop.mango.com/de/damen/mutzen-und-handschuhe_c21062625', 'https://shop.mango.com/de/damen/pyjamas_c37765897', 'https://shop.mango.com/de/damen/rocke_c20673898', 'https://shop.mango.com/de/damen/schals-und-tucher_c12854318', 'https://shop.mango.com/de/damen/schmuck_c23394502', 'https://shop.mango.com/de/damen/schuhe_c10336952', 'https://shop.mango.com/de/damen/shirts---tops_c66796663', 'https://shop.mango.com/de/damen/shorts_c13128150', 'https://shop.mango.com/de/damen/sonnenbrillen_c98638283', 'https://shop.mango.com/de/damen/sportkleidung_c19503847', 'https://shop.mango.com/de/damen/strickjacken---pullover_c18200786', 'https://shop.mango.com/de/damen/sweatshirts_c12454089', 'https://shop.mango.com/de/damen/taschen_c18162733', 'https://shop.mango.com/de/damen/unterwasche-und-lingerie_c11690027', 'https://shop.mango.com/de/damen/weitere-accessoires_c10140832', 'https://shop.mango.com/de/herren/armbander_c15710282', 'https://shop.mango.com/de/herren/badehosen_c30599202', 'https://shop.mango.com/de/herren/bermudashort_c59817148', 'https://shop.mango.com/de/herren/blazer_c14858698', 'https://shop.mango.com/de/herren/edits/family-portraits', 'https://shop.mango.com/de/herren/edits/nachhaltigkeit', 'https://shop.mango.com/de/herren/edits/sneakers', 'https://shop.mango.com/de/herren/edits/tailoring-formula', 'https://shop.mango.com/de/herren/geldborsen_c19081675', 'https://shop.mango.com/de/herren/gurtel-und-hosentrager_c18542801', 'https://shop.mango.com/de/herren/hemden_c10863844', 'https://shop.mango.com/de/herren/highlights/accessoires_d18293934', 'https://shop.mango.com/de/herren/highlights/anzuge_d52175838', 'https://shop.mango.com/de/herren/highlights/best-sellers_d63229427', 'https://shop.mango.com/de/herren/highlights/blazer_d14725620', 'https://shop.mango.com/de/herren/highlights/comfy-collection_d19717538', 'https://shop.mango.com/de/herren/highlights/denim_d18650374', 'https://shop.mango.com/de/herren/highlights/essential-prices_d18747631', 'https://shop.mango.com/de/herren/highlights/exklusiv-online_d14750870', 'https://shop.mango.com/de/herren/highlights/functional-gentleman_d10896007', 'https://shop.mango.com/de/herren/highlights/hemden_d30112580', 'https://shop.mango.com/de/herren/highlights/hosen_d12082825', 'https://shop.mango.com/de/herren/highlights/neu_d28067354', 'https://shop.mango.com/de/herren/highlights/new--now_d78903744', 'https://shop.mango.com/de/herren/highlights/performance_d44128671', 'https://shop.mango.com/de/herren/highlights/promotion_d18340717', 'https://shop.mango.com/de/herren/highlights/re-use-choice_d15323230', 'https://shop.mango.com/de/herren/highlights/sneakers-kollektion_d19398142', 'https://shop.mango.com/de/herren/highlights/sport-collection_d13481778', 'https://shop.mango.com/de/herren/highlights/total-look_d16792783', 'https://shop.mango.com/de/herren/highlights/westen_d17902428', 'https://shop.mango.com/de/herren/hosen_c11949748', 'https://shop.mango.com/de/herren/hute-und-caps_c63186893', 'https://shop.mango.com/de/herren/jacken_c16042202', 'https://shop.mango.com/de/herren/jeans_c23998484', 'https://shop.mango.com/de/herren/krawatten-und-fliegen_c86030314', 'https://shop.mango.com/de/herren/leder_c13997579', 'https://shop.mango.com/de/herren/mantel_c32859776', 'https://shop.mango.com/de/herren/masken_c10453415', 'https://shop.mango.com/de/herren/parfums_c71952558', 'https://shop.mango.com/de/herren/polo-shirts_c20667557', 'https://shop.mango.com/de/herren/rucksacke--und-taschen_c24594145', 'https://shop.mango.com/de/herren/schals_c42692714', 'https://shop.mango.com/de/herren/schuhe_c26231156', 'https://shop.mango.com/de/herren/sonnenbrillen_c35042898', 'https://shop.mango.com/de/herren/sportkleidung_c35955490', 'https://shop.mango.com/de/herren/strickjacken---pullover_c33749244', 'https://shop.mango.com/de/herren/sweatshirts_c71156082', 'https://shop.mango.com/de/herren/t-shirts_c12018147', 'https://shop.mango.com/de/herren/uberhemden_c13028484', 'https://shop.mango.com/de/herren/unterwasche-und-pyjamas_c74722875', 'https://shop.mango.com/de/herren/weitere-accessoires_c17874457', 'https://shop.mango.com/de/home/accessoires_c15092219', 'https://shop.mango.com/de/home/bademantel_c52236690', 'https://shop.mango.com/de/home/badematten_c85184686', 'https://shop.mango.com/de/home/bettbezug_c74618631', 'https://shop.mango.com/de/home/decken-und-bettdecken_c67142604', 'https://shop.mango.com/de/home/decken_c16756016', 'https://shop.mango.com/de/home/duftstabchen_c13195479', 'https://shop.mango.com/de/home/entdecken-sie-die-kollektion_c15573246', 'https://shop.mango.com/de/home/fullungen_c14220192', 'https://shop.mango.com/de/home/fullungen_c64790556', 'https://shop.mango.com/de/home/handtucher_c14144249', 'https://shop.mango.com/de/home/highlights/essential-prices_d35977356', 'https://shop.mango.com/de/home/highlights/eternal-blue_d94461351', 'https://shop.mango.com/de/home/highlights/linen-collection_d13441640', 'https://shop.mango.com/de/home/highlights/neu_d78191035', 'https://shop.mango.com/de/home/highlights/patillatodoa20_d14628547', 'https://shop.mango.com/de/home/highlights/romantic-touch_d9421234', 'https://shop.mango.com/de/home/kerzen_c12486622', 'https://shop.mango.com/de/home/kissenbezuge_c28910550', 'https://shop.mango.com/de/home/kissenbezuge_c64844536', 'https://shop.mango.com/de/home/kopfkissenbezuge_c20038542', 'https://shop.mango.com/de/home/oberlaken_c17215788', 'https://shop.mango.com/de/home/parfums_c14281774', 'https://shop.mango.com/de/home/spannbettlaken_c52730629', 'https://shop.mango.com/de/home/tischwasche_c44087280', 'https://shop.mango.com/de/madchen/bikinis-und-badeanzuge_c18424589', 'https://shop.mango.com/de/madchen/edits/family-portraits', 'https://shop.mango.com/de/madchen/edits/sneakers', 'https://shop.mango.com/de/madchen/hemden_c18370679', 'https://shop.mango.com/de/madchen/highlights/basics_d13616113', 'https://shop.mango.com/de/madchen/highlights/best-sellers_d58408834', 'https://shop.mango.com/de/madchen/highlights/brothers---sisters_d12700054', 'https://shop.mango.com/de/madchen/highlights/denim-collection_d27144189', 'https://shop.mango.com/de/madchen/highlights/denim_d10334373', 'https://shop.mango.com/de/madchen/highlights/destacadoback2school_d18481873', 'https://shop.mango.com/de/madchen/highlights/essential-prices_d21215053', 'https://shop.mango.com/de/madchen/highlights/gold-plated_d13144840', 'https://shop.mango.com/de/madchen/highlights/mum---me_d19352393', 'https://shop.mango.com/de/madchen/highlights/neu_d15971383', 'https://shop.mango.com/de/madchen/highlights/new-now_d15971383', 'https://shop.mango.com/de/madchen/highlights/party-collection_d74469859', 'https://shop.mango.com/de/madchen/highlights/promotion_d77761638', 'https://shop.mango.com/de/madchen/highlights/sneakers-collection_d18512737', 'https://shop.mango.com/de/madchen/highlights/sport_d10047660', 'https://shop.mango.com/de/madchen/hosen_c16674009', 'https://shop.mango.com/de/madchen/jacken_c10281700', 'https://shop.mango.com/de/madchen/jeans_c15188815', 'https://shop.mango.com/de/madchen/kleider_c11805879', 'https://shop.mango.com/de/madchen/leggings_c33314338', 'https://shop.mango.com/de/madchen/mantel_c10792813', 'https://shop.mango.com/de/madchen/masken_c51227748', 'https://shop.mango.com/de/madchen/mode--und-haarschmuck_c15114834', 'https://shop.mango.com/de/madchen/overalls_c56982220', 'https://shop.mango.com/de/madchen/pullover-und-cardigans_c19557162', 'https://shop.mango.com/de/madchen/pyjamas_c21080502', 'https://shop.mango.com/de/madchen/rocke_c90317776', 'https://shop.mango.com/de/madchen/schals-und-mutzen_c34788779', 'https://shop.mango.com/de/madchen/schuhe_c72445239', 'https://shop.mango.com/de/madchen/sweatshirts_c47703127', 'https://shop.mango.com/de/madchen/t-shirts_c19045604', 'https://shop.mango.com/de/madchen/taschen_c11542942', 'https://shop.mango.com/de/madchen/wasche_c68480261', 'https://shop.mango.com/de/madchen/weitere-accessoires_c17719199', 'https://shop.mango.com/de/teena/bikinis-und-badeanzuge_c39151203', 'https://shop.mango.com/de/teena/hemden_c33615460', 'https://shop.mango.com/de/teena/highlights/entdecken-sie-die-kollektion_d16909757', 'https://shop.mango.com/de/teena/highlights/key-trends_d81593715', 'https://shop.mango.com/de/teena/highlights/life-in-layers_d86616047', 'https://shop.mango.com/de/teena/highlights/promotion_d10931066', 'https://shop.mango.com/de/teena/highlights/sport_d20194572', 'https://shop.mango.com/de/teena/highlights/the-indigo-club_d12104868', 'https://shop.mango.com/de/teena/hosen_c39859227', 'https://shop.mango.com/de/teena/jeans_c56576260', 'https://shop.mango.com/de/teena/kleider-und-overalls_c21321422', 'https://shop.mango.com/de/teena/mantel-und-jacken_c14805464', 'https://shop.mango.com/de/teena/pullover-und-cardigans_c16297577', 'https://shop.mango.com/de/teena/rocke_c61367291', 'https://shop.mango.com/de/teena/schuhe_c14487701', 'https://shop.mango.com/de/teena/sportkleidung_c19898462', 'https://shop.mango.com/de/teena/sweatshirts_c17476471', 'https://shop.mango.com/de/teena/t-shirts_c63394451', 'https://shop.mango.com/de/teena/unterwasche-und-pyjamas_c97521904', 'https://shop.mango.com/de/teena/weitere-accessoires_c21010991'] #mango.list_categories("https://shop.mango.com/de/herren")
#    responses = [download_category_(category, mango=mango, sub_categories=sub_categories) for category in tqdm(CATEGORIES, desc="Top-Top")]

#    for cat_response in responses:
#        for response in cat_response:
#            if (response["num_exceptions"]) > 0:
#                print(response)
#            print("-" * 16)

