import pygame #pygameライブラリの読み込み(ゲーム制作用で、画面描画・音・入力処理などを簡単に扱える)
import sys #Pythonのsysモジュールを読み込み(sys.exit()などを使ってプログラムを終了させる)
import json #JSONファイルの読み書きをするためのモジュール(ランキングやタイムをファイルに保存・読み出しする)
import os #ファイルやディレクトリの存在確認など、OSに関連する操作(os.path.existsなど)に使う
import time #時間を測定したり、現在時刻を取得したりするために使う(クリアタイムの計測などで使う)
import random
from player import Player
from enemy import Enemy
from enemy2 import Enemy2

SCORE_FILE = "scores.json" 
TIME_FILE = "times.json"
MAX_RANKING = 5
CLEAR_SCORE = 10 #ステージごとのクリア点数

class Game: #Gameクラスの定義(ゲーム全体の状態や処理を管理する中心となるクラス)
    def __init__(self, screen, width, height): #Gameクラスの初期化メソッド(コンストラクタ)→画面(screen)、画面の横幅(width)、高さ(height)を受け取る
        self.screen = screen #描画対象の画面(pygame.display.set_mode(...)で作ったもの)を保存
        self.width = width #ゲーム画面の横幅と高さを記憶(座標計算などで使用)
        self.height = height
        self.font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 28)
        self.small_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 22)
        self.large_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 48)
        self.title_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 48)
        self.medium_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 34)

        self.player = Player(width, height) #プレイヤーキャラクターを生成(引数は画面サイズ)
        self.player_group = pygame.sprite.Group(self.player) #プレイヤーをGroupにまとめる(描画・当たり判定の処理使用)
        self.bullet_group = pygame.sprite.Group() 
        self.enemy_group = pygame.sprite.Group()
        self.enemy2_group = pygame.sprite.Group()

        self.score = 0 #現在のスコア
        self.stage = 1 #現在のステージ番号(1から始まる)
        self.game_over = False #ゲームオーバー状態かどうか
        self.stage_clear = False #現在のステージがクリアされたか
        self.game_clear = False #最終ステージ(ステージ3)までクリアしたか
        self.running = False #ゲーム中かどうか(開始前は False)
        self.name_input = "" #プレイヤーの名前入力用変数(最初は空)
        self.score_saved = False #スコアがすでに保存されたかどうかを管理するフラグ
        self.time_saved = False #タイムが保存されたかどうかを管理するフラグ
        self.ranking = self.load_scores() #保存済みのスコアランキングを読み込み
        self.time_ranking = self.load_times() #保存済みのクリアタイムランキングを読み込み
        self.start_time = None #ゲームの開始時間(タイマー測定用)
        self.clear_time = None #ゲームクリアにかかった時間(クリア時にセット)

        self.enemy_spawn_timer = 0 #敵を出現させる間隔を制御するためのカウンター

        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
        self.game_over_sound = pygame.mixer.Sound("assets/sounds/game_over.wav")
        self.clear_sound = pygame.mixer.Sound("assets/sounds/clear.wav")
        self.game_over_played = False
        self.game_over_sound.set_volume(1.0) #音量0.0～1.1
        self.clear_sound.set_volume(1.0)
        self.shoot_sound.set_volume(0.5)
        self.hit_sound.set_volume(0.5)

        #ぴよぴよの初期設定
        #サイズをゲーム中と同じに縮小（たとえば 50x50）
        loaded_image = pygame.image.load("assets/images/piyopiyo2.png").convert_alpha() #convert_alpha()画像にアルファチャンネル(透明度)を含む場合、透過を正しく扱える
        self.piyo_image = pygame.transform.scale(loaded_image, (50, 50)) #画像のサイズ(50, 50)
        self.piyo_rect = self.piyo_image.get_rect(center=(self.width // 2, self.height // 2))
        #get_rect()を使って画像のRectオブジェクトを取得し、centerを画面の中央(self.width // 2, self.height // 2)に設定→画像が画面中央に配置

        #ぴよ移動速度（ランダムな方向）
        self.piyo_dx = random.choice([-1, 1]) * random.uniform(0.5, 1.2)
        self.piyo_dy = random.choice([-1, 1]) * random.uniform(0.5, 1.2)
        #random.choice([-1, 1]): -1 または 1をランダムに選び、ぴよぴよが左(-1)または右(1)に進むことができる
        #random.uniform(0.5, 1.2):0.5から1.2の間でランダムな浮動小数点数を生成、ぴよぴよが進む速さがランダムに変わる


    def load_scores(self): #スコアランキングを保存したファイル(SCORE_FILE)から読み込むメソッド
        if os.path.exists(SCORE_FILE): #ファイルが存在しているかをチェック
            with open(SCORE_FILE, "r", encoding="utf-8") as f: #ファイルを「読み取りモード＋UTF-8エンコード」で開く
                return json.load(f) #ファイル内のJSONデータをPythonのリスト(スコアデータのリスト)に変換して返す
        return [] #ファイルが存在しなければ、空のリストを返す(スコア無し状態)

    def load_times(self): #タイムランキング(クリア時間を保存したファイル(TIME_FILE)から読み込む
        if os.path.exists(TIME_FILE):
            with open(TIME_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return [] #スコアと同様の処理：存在すれば読み込む、なければ空リストを返す

    def save_score(self): #プレイヤーのスコアを保存するメソッド
        if self.score_saved: #すでに保存済みなら何もしない(重複保存防止)
            return
        self.score_saved = True #スコア保存済みフラグをTrueにする
        self.ranking.append({"name": self.name_input, "score": self.score}) #入力された名前とスコアを辞書で追加(例：{"name": "eri", "score": 20}）【下に追記】
        self.ranking = sorted(self.ranking, key=lambda x: x["score"], reverse=True)[:MAX_RANKING] #スコアの高い順に並べ直し、上位MAX件(例：5件)だけ残す
        with open(SCORE_FILE, "w", encoding="utf-8") as f: #スコアランキングをJSON形式でファイルに保存
            json.dump(self.ranking, f, ensure_ascii=False, indent=2) #jsonモジュールのdump()関数は、Pythonのデータ(辞書やリスト)をJSONとしてファイルに書き込む

    def save_time(self): #ゲームクリア時間の保存
        if self.time_saved or self.clear_time is None: #すでに保存済みか、クリア時間がないなら処理しない
            return
        self.time_saved = True #保存フラグを立てる(2回保存しないように)
        self.time_ranking.append({"name": self.name_input, "time": round(self.clear_time, 2)}) #名前とクリア時間(小数2桁)をランキングリストに追加
        self.time_ranking = sorted(self.time_ranking, key=lambda x: x["time"])[:MAX_RANKING] #時間の早い順に並べて上位だけ(MAX_RANKING)残す
        with open(TIME_FILE, "w", encoding="utf-8") as f: #時間ランキングをファイルに保存(日本語OK)
            json.dump(self.time_ranking, f, ensure_ascii=False, indent=2)

    def handle_input(self, event): #プレイヤーのキー入力処理
        if not self.running: #ゲーム開始前、名前入力中の処理
            if event.type == pygame.KEYDOWN: #キーが押された時の処理
                if event.key == pygame.K_BACKSPACE: #バックスペースで1文字削除
                    self.name_input = self.name_input[:-1]
                elif event.key == pygame.K_RETURN: #エンターでゲーム開始、開始時間を記録
                    self.running = True
                    self.start_time = time.time()
                elif event.unicode.isprintable():
                    if len(self.name_input) < 8:
                        self.name_input += event.unicode
        elif self.stage_clear: #ステージをクリアした直後の処理
            if event.type == pygame.KEYDOWN: #キーが押されたとき
                if event.key == pygame.K_y: #「Y」で次のステージへ
                    self.next_stage()
                elif event.key == pygame.K_q: #「Q」でゲーム終了
                    pygame.quit()
                    sys.exit()
        elif not self.game_over and not self.game_clear: #ゲームオーバーでもクリア後でもない通常プレイ中
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #スペースキーで弾を発射
                bullet = self.player.shoot()
                self.bullet_group.add(bullet)
                self.shoot_sound.play() #効果音鳴らす
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: #「R」でゲーム再スタート
                    self.restart_game()
                elif event.key == pygame.K_q: #「Q」でゲームを終了する
                    pygame.quit()
                    sys.exit()

    def update(self, keys):
        if not self.running or self.game_over or self.stage_clear: #ゲームが動いていない、終了済み、またはステージクリア中なら処理しない
            return
        self.player_group.update(keys) #プレイヤーや弾の状態を更新
        self.bullet_group.update()

        self.enemy_spawn_timer += 1 #敵の出現タイミングを管理するタイマーを進める

        if self.stage >= 1: #ステージ1以上で、敵が3体未満かつ120フレームごとに1体出現【下に追記】
            if len(self.enemy_group) < 3 and self.enemy_spawn_timer % 120 == 0:
                self.enemy_group.add(Enemy(self.width))
        if self.stage >= 2: #ステージ2以上なら、通常敵が5体未満で100フレームごとに追加、強敵も最大2体まで追加
            if len(self.enemy_group) < 5 and self.enemy_spawn_timer % 100 == 0:
                self.enemy_group.add(Enemy(self.width))
            if len(self.enemy2_group) < 2 and self.enemy_spawn_timer % 150 == 0:
                self.enemy2_group.add(Enemy2(self.width))
        if self.stage >= 3: #ステージ3以上なら敵がもっと頻繁に、多く出現（より難易度が高い）
            if len(self.enemy_group) < 5 and self.enemy_spawn_timer % 100 == 0:
                self.enemy_group.add(Enemy(self.width))
            if len(self.enemy2_group) < 3 and self.enemy_spawn_timer % 130 == 0:
                self.enemy2_group.add(Enemy2(self.width, speed_up=True))

        for enemy in self.enemy_group: #敵がプレイヤーを突破したらゲームオーバー＋スコア保存
            if enemy.update():
                self.game_over = True
                self.save_score()
        for enemy2 in self.enemy2_group: #強敵も同様にチェック
            if enemy2.update():
                self.game_over = True
                self.save_score()

        hits1 = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, True) #弾と敵がぶつかったかを判定(Trueは弾も敵も消す)【下に追記】
        hits2 = pygame.sprite.groupcollide(self.bullet_group, self.enemy2_group, True, True)
        self.score += (len(hits1) + len(hits2)) * 2 #倒した敵1体につきスコア+2点
        if hits1:
            self.hit_sound.play() #当たった音鳴らす
        if hits2:
            self.hit_sound.play()

        if self.score >= CLEAR_SCORE: #スコアがCLEAR_SCOREに到達したらステージクリア判定！
            if self.stage < 3: #ステージ1または2なら、次ステージへ進む準備をする
                self.stage_clear = True
            else:
                self.clear_time = time.time() - self.start_time #ステージ3ならゲームクリア扱いにして、時間を記録＆保存
                self.game_clear = True
                self.save_time()

        #プレイヤーに敵が当たったら即ゲームオーバー＋スコア保存【下に追記】
        if pygame.sprite.spritecollideany(self.player, self.enemy_group) or pygame.sprite.spritecollideany(self.player, self.enemy2_group): 
            self.game_over = True
            self.save_score()
            
        if self.game_clear: #ゲームをクリアしたら、プレイヤーを画面中央へゆっくり移動させる演出(飛び上がるイメージ)
            target_x = self.width // 2
            target_y = self.height // 2
            speed = 2

            #横方向(X軸)の移動
            if self.player.rect.centerx < target_x: #プレイヤーが目標より左にいる場合→speed分だけ右に動かす(ただし、行きすぎないようにminで調整)
                self.player.rect.centerx = min(self.player.rect.centerx + speed, target_x)
            elif self.player.rect.centerx > target_x: #プレイヤーが目標より右にいる場合→speed分だけ左に動かす(行きすぎ防止にmaxを使用)
                self.player.rect.centerx = max(self.player.rect.centerx - speed, target_x)
            #横方向(y軸)の移動
            if self.player.rect.centery < target_y:
                self.player.rect.centery = min(self.player.rect.centery + speed, target_y)
            elif self.player.rect.centery > target_y:
                self.player.rect.centery = max(self.player.rect.centery - speed, target_y) 

    def draw(self): #ゲームが始まっていない場合(=スタート画面のとき)は、draw_start_screenを描画して処理を終了
        if not self.running:
            self.draw_start_screen()
            return

        #背景とキャラの描画
        self.screen.fill((173, 216, 230))
        self.player_group.draw(self.screen)
        self.bullet_group.draw(self.screen)
        self.enemy_group.draw(self.screen)
        self.enemy2_group.draw(self.screen)

        #現在のスコアとステージ番号を左上に表示
        score_text = self.font.render(f"Score: {self.score}", True, (102,102,153))
        stage_text = self.font.render(f"Stage: {self.stage}", True, (255,153,0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(stage_text, (10, 50))

        if self.stage_clear: #self.scoreがクリア条件(CLEAR_SCORE)に達したらself.stage_clearがTrueになる
            self.draw_stage_clear() #→ここでdraw_stage_clear()を呼び出しステージクリア演出を表示
        elif self.game_clear: #最終ステージをクリアした場合の処理
            if not self.game_over_played: #「ゲームオーバーまたはクリア時の効果音がまだ再生されていないか」をチェック→self.game_over_playedがFalseのときだけ、以下の処理を行う
                self.clear_sound.play() #clear音ならす
                self.game_over_played = True #サウンドを再生済みと記録し、これで何度も再生されるのを防ぐ(1回だけ鳴るようにするため)
            self.draw_final_clear() #ゲームクリアの画面(「おめでとう！」など）を描画する関数を呼び出す
        elif self.game_over: #ゲームオーバーになったときの演出と表示
            if not self.game_over_played: #ゲームオーバーのサウンドがまだ再生されていないか確認
                self.game_over_sound.play() #ゲームオーバー音
                self.game_over_played = True #Falseの場合のみ、1回だけ効果音を鳴らす(音を1度鳴らしたら、次からは鳴らさないようにフラグをTrueに設定)
            self.draw_game_over() #「GAME OVER」画面を描画します(テキストやリトライの案内など)

    def draw_start_screen(self):

        #ぴよぴよ
        # 少しずつ方向を変化（自然なふらふら感）
        self.piyo_dx += random.uniform(-0.1, 0.1)
        self.piyo_dy += random.uniform(-0.1, 0.1)

        # 最大速度を制限（速くなりすぎないように）
        max_speed = 1.2
        self.piyo_dx = max(-max_speed, min(max_speed, self.piyo_dx)) #-1.2 と 1.2 の範囲
        self.piyo_dy = max(-max_speed, min(max_speed, self.piyo_dy))

        # 移動
        self.piyo_rect.x += self.piyo_dx #ぴよぴよの位置をpiyo_dxとpiyo_dyを使って移動
        self.piyo_rect.y += self.piyo_dy

        # 画面の端で壁で跳ね返り
        if self.piyo_rect.left <= 0 or self.piyo_rect.right >= self.width: #左端が画面の左端(x = 0)に到達したときにTrue 
            self.piyo_dx *= -1 #（self.piyo_dx）を反転させる処理
        if self.piyo_rect.top <= 0 or self.piyo_rect.bottom >= self.height:
            self.piyo_dy *= -1

        # 描画（文字の後ろにしたい場合はここを最初に）
        self.screen.blit(self.piyo_image, self.piyo_rect)

        shooting_game_text = self.small_font.render("シューティングゲーム", True, (255, 200, 200))
        self.screen.blit(shooting_game_text, (self.width // 2 - shooting_game_text.get_width() // 2, 170))

        title = self.title_font.render("ぴよぴよ戦士", True, (255, 200, 200)) #True はアンチエイリアス(文字を滑らかにする)設定【下に追記】
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 200))#blitレンダリングされた文字や画像を表示(中央揃えの縦位置200)

        input_text = self.font.render(f"お名前（英文字）: 【 {self.name_input} 】", True, (255, 255, 255))
        self.screen.blit(input_text, (self.width // 2 - input_text.get_width() // 2, 300))

        start_text = self.font.render("お名前を入力してEnterキーでスタート", True, (200, 255, 200))
        self.screen.blit(start_text, (self.width // 2 - start_text.get_width() // 2, 350))

        instructions_text = self.small_font.render("矢印キーでぴよが移動　スペースキーで発射", True, (200, 255, 200))
        self.screen.blit(instructions_text, (self.width // 2 - instructions_text.get_width() // 2, self.height // 2 + 100))

    def draw_stage_clear(self):
        clear_text = self.large_font.render("STAGE CLEAR!", True, (0,102,204))
        next_text = self.font.render("Yキーで次のステージ、Qキーで終了", True, (102,102,153))
        self.screen.blit(clear_text, (self.width // 2 - clear_text.get_width() // 2, self.height // 2 - 100))
        self.screen.blit(next_text, (self.width // 2 - next_text.get_width() // 2, self.height // 2))

    def draw_game_over(self):
        over_text = self.large_font.render("GAME OVER", True, (234,84,93))
        self.screen.blit(over_text, (self.width // 2 - over_text.get_width() // 2, self.height // 2 - 100))

        restart_text = self.font.render("Rキーで再チャレンジ、Qキーで終了", True, (102,102,153))
        self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2))

    def draw_final_clear(self): #ゲームを完全クリアしたときの画面表示処理
        if not self.game_over_played: #もしself.game_over_playedがFalse(=まだ音が再生されていない)なら
            self.clear_sound.play() #ゲームクリア時の音
            self.game_over_played = True #音が再生されたのでgame_over_playedをTrueにして「もう一度再生しない」ように

        congrats_text = self.medium_font.render(f"{self.name_input} さん Congratulations!", True, (233,84,107))
        congrats_main = self.title_font.render("GAME CLEAR!", True, (234,84,93))

        #GAME CLEAR! を画面中央上に表示→文字の幅を考慮して「中央寄せ」になるように調整【下に追記】
        self.screen.blit(congrats_main, (self.width // 2 - congrats_main.get_width() // 2, self.height // 2 - 160))
        #「○○ さん Congratulations!」のテキストを、その下（中央より少し上）に表示
        self.screen.blit(congrats_text, (self.width // 2 - congrats_text.get_width() // 2, self.height // 2 - 100))

        # 上位タイムとランキングの表示位置を少し上に調整
        top_text = self.small_font.render("上位タイム", True, (255,153,0))
        self.screen.blit(top_text, (self.width // 2 - top_text.get_width() // 2, self.height // 2 + 20))

        for i, entry in enumerate(self.time_ranking[:5]):#上位タイム(最大5件)をループで表示していく→iは順位(0〜4)、entryは名前とタイムが入った辞書
            time_entry = self.small_font.render(f"{i+1}. {entry['name']} : {entry['time']}秒", True, (102,102,153)) #各プレイヤーの順位、名前、クリアタイムを描画用に作成
            self.screen.blit(time_entry, (self.width // 2 - time_entry.get_width() // 2, self.height // 2 + 50 + i * 30)) #ランキングの各エントリーを縦にずらして表示
            #→i * 30で表示位置が下にずれていくことで、行ごとにスペースができる

    def next_stage(self): #次のステージに進む処理を行うメソッド
        self.stage += 1 #現在のステージ番号を1増やして、次のステージに進む
        self.stage_clear = False #「ステージクリア状態」を解除し、次のステージに進む準備
        self.enemy_group.empty() #画面上の敵(通常敵・強敵)をすべて削除して、ステージをリセット
        self.enemy2_group.empty()
        self.score = 0 #ステージごとにスコアをリセット(次のステージは0点から開始)

    def restart_game(self): #ゲーム全体を最初からやり直す処理を行うメソッド
        self.score = 0 #スコアを0に戻す
        self.stage = 1 #ステージを最初(1)に戻す
        self.game_over = False #「ゲームオーバー」「ステージクリア」「ゲームクリア」の状態をすべてリセット
        self.stage_clear = False
        self.game_clear = False
        self.score_saved = False #スコアやタイムの保存状態をリセット→再プレイでも新たに記録できるようになる
        self.time_saved = False
        self.enemy_group.empty() #敵キャラとプレイヤーの弾をすべて削除して、クリーンな状態に戻す
        self.enemy2_group.empty()
        self.bullet_group.empty()
        self.player.rect.centerx = self.width // 2 #プレイヤーの位置を画面下中央にリセット
        self.player.rect.bottom = self.height - 30
        self.start_time = time.time() #ゲームの再スタート時点の時刻を記録します(タイム測定の開始)
        self.clear_time = None #クリアタイムを初期化(まだクリアしていない状態に戻す)
        self.game_over_played = False #「ゲームオーバー音」などの再生フラグをリセットして、再度音が鳴るようにする


'''
★def save_score(self):の
self.ranking = sorted(self.ranking, key=lambda x: x["score"], reverse=True)
(1)sorted(...):
→ リストを並び替える関数(元のリストは変更せず、新しい並びのリストを返す)
(2)key=lambda x: x["score"]:
→ x は ranking リストの中の各要素（辞書）を表す
たとえば {"name": "たろう", "score": 120} など
その中の score の値を並び替えの基準にする
(3)reverse=True:
→ 降順(大きい→小さい)に並び替える Falseなら昇順(小さい→大きい)

★def update(self, keys):の
if self.stage >= 1: #ステージ1以上で、敵が3体未満かつ120フレームごとに1体出現
            if len(self.enemy_group) < 3 and self.enemy_spawn_timer % 120 == 0:
                self.enemy_group.add(Enemy(self.width))
(1)if len(self.enemy_group) < 3
現在、画面上に存在する通常の敵（Enemy）が3体未満であるかをチェック
つまり、敵の数が制限以下なら次の条件もチェック
(2)and self.enemy_spawn_timer % 120 == 0
ゲーム内でカウントされているenemy_spawn_timerが120の倍数(=2秒ごと程度)であるかをチェック
enemy_spawn_timer は毎フレーム1ずつ増えているので、120フレーム ≒ 約2秒
(3)self.enemy_group.add(Enemy(self.width))
上の2つの条件を満たす場合に、新しい敵（Enemy）を生成して追加

★def update(self, keys):の
hits1 = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, True) 
(1)pygame.sprite.groupcollide(...):
→ 2つのスプライトグループ(ここでは弾と敵)で、衝突しているものを探す関数
(2)self.bullet_group:
→ 衝突の判定元グループ（プレイヤーが撃った弾）
(3)self.enemy_group:
→ 衝突の判定対象グループ（敵キャラ）
(4)True:
→ 衝突した弾を削除する
(5)True:
→ 衝突した敵も削除する
(6)hits1:
→ 衝突した弾と敵の情報を持った辞書が返る(あとでスコア加算などに使える)

★def update(self, keys):の
if pygame.sprite.spritecollideany(self.player, self.enemy_group) or pygame.sprite.spritecollideany(self.player, self.enemy2_group): 
            self.game_over = True
            self.save_score()
(1)pygame.sprite.spritecollideany(...):
→ 指定したスプライト(ここでは self.player)が、指定したグループのどれか1つとでもぶつかっていればTrueを返す関数
(2)self.player:
→ プレイヤーキャラ
(3)self.enemy_group, self.enemy2_group:
→ 敵のグループ(どちらかの敵にぶつかったらアウト)
(4)or:
→ どちらか一方と衝突していれば、条件成立

★def update(self, keys):の
if self.player.rect.centerx < target_x:
                self.player.rect.centerx = min(self.player.rect.centerx + speed, target_x)
プレイヤーが目標より左にいる場合→speed分だけ右に動かす(ただし、行きすぎないようにminで調整)
(1)if self.player.rect.centerx < target_x:
→ プレイヤーのX座標(中心)が目標位置target_xより左にいるかをチェック
(2)self.player.rect.centerx = min(self.player.rect.centerx + speed, target_x)
→ プレイヤーを右に「speed ピクセル」動かす→min(..., target_x)にすることで、目標を超えないように制限
<例>
・centerx = 200, target_x = 250, speed = 5 の場合 → centerx は205に
・centerx = 248 のとき → centerx + 5 = 253 だが、min(253, 250) → 250に

★def draw_start_screen(self):
renderは、文字(テキスト)を画像として描くためのメソッド
Pygameでは、テキストは直接画面に表示できないので、まず「画像（Surface）」に変換してからblitで描画

★def draw_final_clear(self):
self.screen.blit(congrats_main, (self.width // 2 - congrats_main.get_width() // 2, self.height // 2 - 160))
「GAME CLEAR! の文字を画面の中央やや上に、ぴったり真ん中に揃えて表示している」
(1)self.screen.blit(...)
→ 画面(self.screen)に画像や文字などの描画
(2)congrats_main
→ これは前の行などでrender()によって作られた「GAME CLEAR!」というテキスト画像
(3)(self.width // 2 - congrats_main.get_width() // 2, self.height // 2 - 160)
→ 表示する位置
(4)self.width // 2 は画面の 中央X座標
(5)congrats_main.get_width() // 2 は「文字の幅の半分」なので、これを引くと 中央にぴったり合わせて表示
(6)self.height // 2 - 160 は縦方向の位置で、画面中央より 上に160ピクセル 移動

★def draw_final_clear(self):
 for i, entry in enumerate(self.time_ranking[:5]):
    time_entry = self.small_font.render(f"{i+1}. {entry['name']} : {entry['time']}秒", True, (102,102,153)) 
    self.screen.blit(time_entry, (self.width // 2 - time_entry.get_width() // 2, self.height // 2 + 50 + i * 30))
このコードは上位5人のタイムをランキング形式で表示するための部分でenumerateを使って、time_rankingの上位5件(最大5人分)を表示
各プレイヤーの順位、名前、タイムを表示するためにrenderでテキストを作成し、blitで画面に描画
(1)enumerate(self.time_ranking[:5])
→ self.time_ranking の先頭5つのエントリをループ
(2)iはその順位(0〜4)、entryは名前とクリアタイムが格納された辞書
(3)time_entryで表示するテキスト<例：1. PlayerName : 3.45秒>を生成
(4)self.screen.blit() で画面上に描画
※0 + i * 30 はタイムランキングの各順位を画面に表示する際の縦方向の位置を計算
50 は最初のアイテム(1位)の縦座標を決めており、基準となる位置
i * 30 は各順位が30ピクセル間隔で下に表示される
i は順位(0〜4)つまり1位のiは 0、2位のiは 1...と増えていく
これにより、50 + 0 * 30 で1位が50の位置に、50 + 1 * 30 で2位が80の位置に、と30ピクセルごとに順位が下がる形
順位が5位(i=4)になると 50 + 4 * 30 = 170という位置になる
'''

'''
★コメントなしのcodeだけ必要な時
import pygame
import sys
import json
import os
import time
from player import Player
from enemy import Enemy
from enemy2 import Enemy2

SCORE_FILE = "scores.json"
TIME_FILE = "times.json"
MAX_RANKING = 5
CLEAR_SCORE = 5  # ステージごとのクリア点数

class Game:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 28)
        self.small_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 22)
        self.large_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 48)
        self.title_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 48)
        self.medium_font = pygame.font.Font("assets/fonts/Zen_Maru_Gothic/ZenMaruGothic-Regular.ttf", 34)

        self.player = Player(width, height)
        self.player_group = pygame.sprite.Group(self.player)
        self.bullet_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy2_group = pygame.sprite.Group()

        self.score = 0
        self.stage = 1
        self.game_over = False
        self.stage_clear = False
        self.game_clear = False
        self.running = False
        self.name_input = ""
        self.score_saved = False
        self.time_saved = False
        self.ranking = self.load_scores()
        self.time_ranking = self.load_times()
        self.start_time = None
        self.clear_time = None

        self.enemy_spawn_timer = 0

        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
        self.game_over_sound = pygame.mixer.Sound("assets/sounds/game_over.wav")
        self.clear_sound = pygame.mixer.Sound("assets/sounds/clear.wav")
        self.game_over_played = False
        self.game_over_sound.set_volume(1.0)
        self.clear_sound.set_volume(0.8)
        self.shoot_sound.set_volume(0.5)
        self.hit_sound.set_volume(0.5)

    def load_scores(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def load_times(self):
        if os.path.exists(TIME_FILE):
            with open(TIME_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_score(self):
        if self.score_saved:
            return
        self.score_saved = True
        self.ranking.append({"name": self.name_input, "score": self.score})
        self.ranking = sorted(self.ranking, key=lambda x: x["score"], reverse=True)[:MAX_RANKING]
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.ranking, f, ensure_ascii=False, indent=2)

    def save_time(self):
        if self.time_saved or self.clear_time is None:
            return
        self.time_saved = True
        self.time_ranking.append({"name": self.name_input, "time": round(self.clear_time, 2)})
        self.time_ranking = sorted(self.time_ranking, key=lambda x: x["time"])[:MAX_RANKING]
        with open(TIME_FILE, "w", encoding="utf-8") as f:
            json.dump(self.time_ranking, f, ensure_ascii=False, indent=2)

    def handle_input(self, event):
        if not self.running:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self.running = True
                    self.start_time = time.time()
                elif event.unicode.isprintable():
                    if len(self.name_input) < 8:
                        self.name_input += event.unicode
        elif self.stage_clear:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self.next_stage()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        elif not self.game_over and not self.game_clear:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullet = self.player.shoot()
                self.bullet_group.add(bullet)
                self.shoot_sound.play()
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

    def update(self, keys):
        if not self.running or self.game_over or self.stage_clear:
            return
        self.player_group.update(keys)
        self.bullet_group.update()

        self.enemy_spawn_timer += 1

        if self.stage >= 1:
            if len(self.enemy_group) < 3 and self.enemy_spawn_timer % 120 == 0:
                self.enemy_group.add(Enemy(self.width))
        if self.stage >= 2:
            if len(self.enemy_group) < 5 and self.enemy_spawn_timer % 100 == 0:
                self.enemy_group.add(Enemy(self.width))
            if len(self.enemy2_group) < 2 and self.enemy_spawn_timer % 150 == 0:
                self.enemy2_group.add(Enemy2(self.width))
        if self.stage >= 3:
            if len(self.enemy_group) < 6 and self.enemy_spawn_timer % 80 == 0:
                self.enemy_group.add(Enemy(self.width))
            if len(self.enemy2_group) < 3 and self.enemy_spawn_timer % 130 == 0:
                self.enemy2_group.add(Enemy2(self.width, speed_up=True))

        for enemy in self.enemy_group:
            if enemy.update():
                self.game_over = True
                self.save_score()
        for enemy2 in self.enemy2_group:
            if enemy2.update():
                self.game_over = True
                self.save_score()

        hits1 = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, True)
        hits2 = pygame.sprite.groupcollide(self.bullet_group, self.enemy2_group, True, True)
        self.score += (len(hits1) + len(hits2)) * 2
        if hits1:
            self.hit_sound.play()
        if hits2:
            self.hit_sound.play()

        if self.score >= CLEAR_SCORE:
            if self.stage < 3:
                self.stage_clear = True
            else:
                self.clear_time = time.time() - self.start_time
                self.game_clear = True
                self.save_time()

        if pygame.sprite.spritecollideany(self.player, self.enemy_group) or pygame.sprite.spritecollideany(self.player, self.enemy2_group):
            self.game_over = True
            self.save_score()
            
        if self.game_clear:
            target_x = self.width // 2
            target_y = self.height // 2
            speed = 2

            if self.player.rect.centerx < target_x:
                self.player.rect.centerx = min(self.player.rect.centerx + speed, target_x)
            elif self.player.rect.centerx > target_x:
                self.player.rect.centerx = max(self.player.rect.centerx - speed, target_x)

            if self.player.rect.centery < target_y:
                self.player.rect.centery = min(self.player.rect.centery + speed, target_y)
            elif self.player.rect.centery > target_y:
                self.player.rect.centery = max(self.player.rect.centery - speed, target_y) 

    def draw(self):
        if not self.running:
            self.draw_start_screen()
            return

        self.screen.fill((173, 216, 230))
        self.player_group.draw(self.screen)
        self.bullet_group.draw(self.screen)
        self.enemy_group.draw(self.screen)
        self.enemy2_group.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (102,102,153))
        stage_text = self.font.render(f"Stage: {self.stage}", True, (255,153,0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(stage_text, (10, 50))

        if self.stage_clear:
            self.draw_stage_clear()
        elif self.game_clear:
            if not self.game_over_played:
                self.clear_sound.play()
                self.game_over_played = True
            self.draw_final_clear()
        elif self.game_over:
            if not self.game_over_played:
                self.game_over_sound.play()
                self.game_over_played = True
            self.draw_game_over()

    def draw_start_screen(self):
        title = self.title_font.render("ぴよぴよ戦士", True, (255, 200, 200))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 200))

        input_text = self.font.render(f"名前: {self.name_input}", True, (255, 255, 255))
        self.screen.blit(input_text, (self.width // 2 - input_text.get_width() // 2, 300))

        start_text = self.font.render("Enterキーでスタート", True, (200, 255, 200))
        self.screen.blit(start_text, (self.width // 2 - start_text.get_width() // 2, 350))

    def draw_stage_clear(self):
        clear_text = self.large_font.render("STAGE CLEAR!", True, (0,102,204))
        next_text = self.font.render("Yキーで次のステージ、Qキーで終了", True, (102,102,153))
        self.screen.blit(clear_text, (self.width // 2 - clear_text.get_width() // 2, self.height // 2 - 100))
        self.screen.blit(next_text, (self.width // 2 - next_text.get_width() // 2, self.height // 2))

    def draw_game_over(self):
        over_text = self.large_font.render("GAME OVER", True, (234,84,93))
        self.screen.blit(over_text, (self.width // 2 - over_text.get_width() // 2, self.height // 2 - 100))

        restart_text = self.font.render("Rキーで再チャレンジ、Qキーで終了", True, (102,102,153))
        self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2))

    def draw_final_clear(self):
        if not self.game_over_played:
            self.clear_sound.play()
            self.game_over_played = True

        congrats_text = self.medium_font.render(f"{self.name_input} さん Congratulations!", True, (233,84,107))
        congrats_main = self.title_font.render("GAME CLEAR!", True, (234,84,93))

        self.screen.blit(congrats_main, (self.width // 2 - congrats_main.get_width() // 2, self.height // 2 - 160))
        self.screen.blit(congrats_text, (self.width // 2 - congrats_text.get_width() // 2, self.height // 2 - 100))

        # 上位タイムとランキングの表示位置を少し上に調整
        top_text = self.small_font.render("上位タイム", True, (255,153,0))
        self.screen.blit(top_text, (self.width // 2 - top_text.get_width() // 2, self.height // 2 + 20))

        for i, entry in enumerate(self.time_ranking[:5]):
            time_entry = self.small_font.render(f"{i+1}. {entry['name']} : {entry['time']}秒", True, (102,102,153))
            self.screen.blit(time_entry, (self.width // 2 - time_entry.get_width() // 2, self.height // 2 + 50 + i * 30))

    def next_stage(self):
        self.stage += 1
        self.stage_clear = False
        self.enemy_group.empty()
        self.enemy2_group.empty()
        self.score = 0

    def restart_game(self):
        self.score = 0
        self.stage = 1
        self.game_over = False
        self.stage_clear = False
        self.game_clear = False
        self.score_saved = False
        self.time_saved = False
        self.enemy_group.empty()
        self.enemy2_group.empty()
        self.bullet_group.empty()
        self.player.rect.centerx = self.width // 2
        self.player.rect.bottom = self.height - 30
        self.start_time = time.time()
        self.clear_time = None
        self.game_over_played = False

'''