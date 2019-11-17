# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 19:38:14 2019

AIに食わせる画像を探すためにpixivpyをやります。
タグで探せるようにつくります。
とりあえずクラス化しました。
"""

from pixivpy3 import AppPixivAPI
from pixivpy3 import PixivAPI
import os

class PixivDownloader :
    
    def __init__(self):
        self.pixiv           = PixivAPI()
        self.app_pixiv       = AppPixivAPI()
        
    def login(self, user_id, user_password):
        return self.pixiv.login(user_id, user_password)  
    
    def download(self, save_num, query,
                 search_mode  = "text",
                 search_types = ["illustration"],
                 save_path    = "C:/Users/"+ os.environ.get("USERNAME") +"/Pictures",
                 worst_score  = 0,
                 worst_views  = 0,
                 worst_favo   = 0,
                 r18_flag     = False,
                 ):
        #　検索
        search_result = self.pixiv.search_works(query, page = 1, per_page = save_num, 
                                                mode = search_mode, types = search_types)
        #　save_num の数ダウンロードしたいが、そもそも画像が少ない場合はあるだけダウンロード
        if save_num > search_result.pagination.total:
            save_num = search_result.pagination.total
        
        #　セーブ先　無ければつくる
        save_path = save_path + "/" + query[0] + "/"
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        
        current_work        = 0
        total_downloaded    = 0
        page_num            = 2
        
        while total_downloaded < save_num:
            if current_work == save_num:
                #　条件不一致で飛ばされるので、不足分を補う為にもう一度読み込み
                
                if search_result.pagination.next == None:
                    #　これ以上読み込めない場合は終了
                    break
                
                current_work  = 0
                search_result = self.pixiv.search_works(query, page = page_num, per_page = save_num, 
                                                        mode = search_mode, types = search_types)
                if save_num > len(search_result.response):
                    save_num = len(search_result.response)
                page_num += 1
            
            work = search_result.response[current_work]
            current_work  += 1
            
            if work.page_count > 1:
                # 複数セット省く
                print("Out "+work.title+":セット")
                continue
            
            if work.stats.score < worst_score:
                #　Scoreによる選別
                continue
            
            if work.stats.views_count < worst_views:
                #　閲覧数による選別
                print("Out "+work.title+":閲覧数")
                continue
            
            if work.stats.favorited_count.public < worst_favo:
                #　いいねによる選別
                print("Out "+work.title+":いいね")
                continue
            
            if r18_flag == (work.age_limit == "all-age"):
                # 年齢制限の有無
                print("Out "+work.title+":年齢制限")
                continue
            
            if os.path.exists(save_path+str(work.id)+"_p0.png") or os.path.exists(save_path+str(work.id)+"_p0.jpg"):
                # 既に同名のファイルがある場合
                print(work.title +" has already downloaded")
                continue
            
            #　Download
            self.pixiv.download(work.image_urls.large, save_path)
            total_downloaded += 1;
            print("Downloaded {0}/{1}".format(total_downloaded, save_num)+':'+str(work.title))

#　使用例
if __name__ == "__main__":
    #　指定するものとか
    save_works_num  = 1000
    favo            = 10
    mode            = ["exact_tag"]
    search_tags     = [["カリオストロ(グラブル)"], ["櫻井桃華"], ["ネロ・クラウディウス"], ["ギルガメッシュ"], ["沙都子"], ["木之本桜"]]
    save_path       = ""
    
    p = PixivDownloader()
    p.login("id", "pass")
    data = []
    for data in search_tags:
        p.download(save_works_num, data, search_mode = mode, save_path=save_path, worst_favo=favo)

    print("Complete!")
