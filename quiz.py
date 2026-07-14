import pygame
import random
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ==========================
# Quizクラス
# ==========================
class Quiz:
    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer


# ==========================
# Buttonクラス
# ==========================
class Button:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, font, text, color):
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        image = font.render(text, True, (0, 0, 0))
        screen.blit(image, (self.rect.x + 20, self.rect.y + 15))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
class Fiftyfifty:
    """
    Fiftyfiftyクラス
    クイズの選択肢を半分に減らすライフライン
    """
    def __init__(self,quiz: Quiz) -> None:
        """
        引数:Quizクラス
        戻り値:なし
        答えの選択肢をQuizクラスから取得、
        現在の選択肢から正解とランダムに選ばれた不正解の選択肢以外を削除
        """
        answer = quiz.answer
        self.choices = [False,False,False,False]
        miss = [0,1,2,3]
        miss.remove(answer)

        self.choices[answer] = True  # Trueの選択肢は残る
        self.choices[random.choice(miss)] = True

    def is_collect(self, index:int) -> list:
        """
        引数:int
        戻り値:list
        イニシャライザで作った消す選択肢のリストを返す
        """
        return self.choices[index]


# ==========================
# QuizGameクラス
# ==========================
class QuizGame:

    def __init__(self):

        pygame.init()

        self.WIDTH = 800
        self.HEIGHT = 600

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("4択クイズ")

        # フォント
        base_dir = os.path.dirname(__file__)
        font_path = os.path.join(
            base_dir,
            "fonts",
            "NotoSansJP-Bold.ttf"
        )

        self.title_font = pygame.font.Font(font_path, 60)
        self.question_font = pygame.font.Font(font_path, 40)
        self.choice_font = pygame.font.Font(font_path, 30)
        self.result_font = pygame.font.Font(font_path, 36)
        self.guide_font = pygame.font.Font(font_path, 24)
        self.timer_font = pygame.font.Font(font_path, 36) #　タイマー用のフォントの追加

        # 色
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (220, 220, 220)
        self.GREEN = (120, 230, 120)
        self.RED = (255, 120, 120)

        # 音
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 同じ階層にある「SE」フォルダへのパスを作成
        se_dir = os.path.join(base_dir, "SE")

        # 効果音ファイルの読み込み
        try:
            self.correct_sound = pygame.mixer.Sound(os.path.join(se_dir, "correct.mp3"))
            self.wrong_sound = pygame.mixer.Sound(os.path.join(se_dir, "wrong.mp3"))
            self.timeup_sound = pygame.mixer.Sound(os.path.join(se_dir, "wrong.mp3"))
            self.fiffif_sound = pygame.mixer.Sound(os.path.join(se_dir, "fiffif.mp3"))
            self.startquiz_sound = pygame.mixer.Sound(os.path.join(se_dir, "startquiz.mp3"))
            
            # 音量調整 (0.0 〜 1.0) ※必要に応じて数値を変更してください
            self.correct_sound.set_volume(0.5)
            self.wrong_sound.set_volume(0.4)
            self.timeup_sound.set_volume(0.4)
            self.fiffif_sound.set_volume(0.7)
            self.startquiz_sound.set_volume(0.5)
            
        except pygame.error as e:
            print(f"音声ファイルの読み込みに失敗しました: {e}")
            # ファイルが見つからない場合などにゲームがクラッシュするのを防ぐ
            self.correct_sound = None
            self.wrong_sound = None
            self.timeup_sound = None
            self.fiffif_sound = None
            self.startquiz_sound = None

        # ゲームの状態管理 ("START", "PLAY", "RESULT")
        self.state = "START"

        # スコアと出題数の管理
        self.score = 0
        self.total_questions = 0
        self.quiz_queue = []

        #　タイマー用の変数
        self.LIMIT_TIME = 10.0
        self.start_time = 0
        self.remaining_time = self.LIMIT_TIME

        # 問題
        self.quizzes = [
            Quiz(
                "日本の首都は？",
                ["大阪", "東京", "福岡", "札幌"],
                1
            ),

            Quiz(
                "Pythonを開発した人物は？",
                [
                    "Guido van Rossum",
                    "Bill Gates",
                    "Steve Jobs",
                    "Linus Torvalds"
                ],
                0
            ),

            Quiz(
                "1 + 1 = ?",
                ["1", "2", "3", "4"],
                1
            ),
            
            Quiz(
                "「カレーの市民」などで知られる芸術家は？",
                ["ラッセン","モネ","ロダン","ゴッホ"],
                2
            ),

            Quiz(
                "四鏡のうち、最も早く成立したのは？",
                ["水鏡","今鏡","増鏡","大鏡"],
                3
            ),

            Quiz(
                "伊藤博文が初代知事を務めた都道府県は？",
                ["兵庫県","山口県","大阪府","鹿児島県"],
                0
            ),

            Quiz(
               "酷暑日は一日の最高気温が摂氏何度から？",
               ["30","35","40","45"],
               2
            ),

            Quiz(
                "クレアチンを構成する3つのアミノ酸ではないものは?",
                ["バリン","アルギニン","グリシン","メチオニン"],
                0
            ),

            Quiz(
                "「星の王子様」の著者は?",
                ["モーパッサン","サルトル","カミュ","サン=テグジュペリ"],
                3
            ),

            Quiz(
                "日本料理でないものはどれ?",
                ["オムライス","水餃子","ドリア","オムライス"],
                1
            ),

            Quiz(
                "次のうち、小学一年生で習う漢字は？",
                ["心","言","今","夕"],
                3
            ),
        ]

        # 4択クイズ用ボタン
        self.buttons = []
        for i in range(4):
            self.buttons.append(
                Button(
                    120,
                    200 + i * 80,
                    560,
                    60
                )
            )

        # スタート画面・リザルト画面用のボタン
        self.start_button = Button(300, 400, 200, 60)
        self.retry_button = Button(260, 420, 280, 60)

        self.current_quiz = None
        self.answered = False
        self.message = ""
        self.selected_choice = None

        self.fifty = None
        self.fifty_used = False

    # --------------------------
    # ゲームの開始・初期化
    # --------------------------
    def start_game(self):
        """
        引数：なし
        戻り値：なし
        スコアの初期化、クイズの問題の複製・シャッフル、問題数の初期化を行いゲームを開始する

        """
        self.score = 0
        self.quiz_queue = self.quizzes.copy()
        random.shuffle(self.quiz_queue)
        self.total_questions = len(self.quiz_queue)
        
        self.state = "PLAY"
        

        self.next_quiz()

    def use_fifty(self):
        """
        50-50を使う関数
        使われたならfifty-usedをTrueにし、2回目の使用を不可能にする。
        """
        if self.fifty_used:
            return  # もし使われているならそのまま出る
        
        if self.fifty is None:
            self.fifty = Fiftyfifty(self.current_quiz)
            if self.timeup_sound:
                self.fiffif_sound.play()
            self.fifty_used = True

    # --------------------------
    # 次の問題
    # --------------------------
    def next_quiz(self):
        """
        引数：なし
        戻り値：なし
        残り問題数が0であればリザルト画面に移動し、そうでなければ複製した問題群から次の1問を抜き出す。
        そのあと回答したかの判定変数と何を選んだかの変数を初期化する
        """
        if len(self.quiz_queue) == 0:
            self.state = "RESULT"
            return

        self.current_quiz = self.quiz_queue.pop(0)
        self.answered = False
        self.message = ""
        self.selected_choice = None

        self.fifty = None
        self.start_time = pygame.time.get_ticks() #　出題したときの時間を記録
        if self.startquiz_sound:
            self.startquiz_sound.play()

    # --------------------------
    # タイマー更新・判定
    # --------------------------
    def update_timer(self):
        """
        未回答の場合に経過時間を計算してカウントダウンし、タイムアップを判定するメソッド
        引数：なし
        戻り値：なし
        """
        if not self.answered:
            elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000
            self.remaining_time = max(0.0, self.LIMIT_TIME - elapsed_seconds)

            #　タイムアップ判定
            if self.remaining_time <= 0:
                self.answered = True
                answer = self.current_quiz.choices[self.current_quiz.answer]
                self.message = f"タイムアップ！　正解は「{answer}」"

                if self.timeup_sound:
                    self.timeup_sound.play()
        else:
            self.remaining_time = 0.0

    # --------------------------
    # 描画
    # --------------------------
    def draw(self):
        """
        引数：なし
        戻り値：なし
        現在の状況がスタートなのかプレイ中なのかリザルトなのかを判断し、それぞれの処理と画面表示を行う
        """
        self.screen.fill(self.WHITE)

        if self.state == "START":
            title = self.title_font.render("4択クイズゲーム", True, self.BLACK)
            self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 180))
            self.start_button.draw(self.screen, self.choice_font, "スタート", self.GRAY)

# <<<<<<< HEAD
        elif self.state == "PLAY":
            question = self.question_font.render(
                self.current_quiz.question,
                True,
                self.BLACK
# =======
        # self.screen.blit(question, (40, 50))

        # #　タイマー表示(問題の上に表示。残り3秒になると文字が赤くなる)
        # timer_color = self.RED if self.remaining_time <= 3.0 else self.BLACK
        # timer_text = self.timer_font.render(
        #     f"残り時間：{self.remaining_time:.1f}秒",
        #     True,
        #     timer_color
        # )
        # self.screen.blit(timer_text, (40,10))

        # for i in range(4):

        #     color = self.GRAY

        #     if self.answered and i == self.current_quiz.answer:
        #         color = self.GREEN

        #     self.buttons[i].draw(
        #         self.screen,
        #         self.choice_font,
        #         self.current_quiz.choices[i],
        #         color
# >>>>>>> C0C25046/timer
            )
            self.screen.blit(question, (40, 50))

            #　タイマー表示(問題の上に表示。残り3秒になると文字が赤くなる)
            timer_color = self.RED if self.remaining_time <= 3.0 else self.BLACK
            timer_text = self.timer_font.render(
                f"残り時間：{self.remaining_time:.1f}秒",
                True,
                timer_color
            )

            self.screen.blit(timer_text, (40,10))

            for i in range(4):
                color = self.GRAY

                if self.fifty is not None:
                    if not self.fifty.is_collect(i):  # もし使わない選択肢なら、この回のループを終了する
                        continue       
                
                if self.answered:
                    if i == self.current_quiz.answer:
                        color = self.GREEN
                    elif i == self.selected_choice:
                        color = self.RED

                self.buttons[i].draw(
                    self.screen,
                    self.choice_font,
                    self.current_quiz.choices[i],
                    color
                )

            result = self.result_font.render(
                self.message,
                True,
                self.RED
            )
            self.screen.blit(result, (40, 505))

            if self.answered:
                guide = self.guide_font.render(
                    "【SPACE】キーを押して次の問題へ",
                    True,
                    self.BLACK
                )
                self.screen.blit(guide, (40, 555))

        elif self.state == "RESULT":
            result_title = self.title_font.render("結果発表", True, self.BLACK)
            self.screen.blit(result_title, (self.WIDTH // 2 - result_title.get_width() // 2, 150))

            score_text = self.question_font.render(
                f"正解数: {self.score} / {self.total_questions}",
                True,
                self.BLACK
            )
            self.screen.blit(score_text, (self.WIDTH // 2 - score_text.get_width() // 2, 280))
            
            self.retry_button.draw(self.screen, self.choice_font, "タイトルへ戻る", self.GRAY)

        pygame.display.flip()

    # --------------------------
    # イベント
    # --------------------------
    def event(self):
        """
        引数：なし
        戻り値：なし
        選択肢をクリックしたときやスタートボタンやスペースキー、スタートに戻るボタンなどをクリックしたときの判定や処理を行う。
        """
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if self.state == "START":
                    if self.start_button.is_clicked(pos):
                        self.start_game()

                elif self.state == "PLAY":
                    if not self.answered:
                        for i in range(4):
                            if self.buttons[i].is_clicked(pos):
                                self.answered = True
                                # 【追加】クリックされたボタンの番号を保存
                                self.selected_choice = i

                                if i == self.current_quiz.answer:
                                    self.message = "正解！"
                                    self.score += 1
                                    if self.correct_sound:
                                        self.correct_sound.play()
                                else:
                                    answer = self.current_quiz.choices[
                                        self.current_quiz.answer
                                    ]
                                    self.message = f"不正解！ 正解は「{answer}」"
                                    if self.wrong_sound:
                                        self.wrong_sound.play()

                elif self.state == "RESULT":
                    if self.retry_button.is_clicked(pos):
                        self.state = "START"

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f:  # Fキーが押されたら50-50を使用
                    self.use_fifty()


                if self.answered:
                    if self.state == "PLAY" and self.answered:
                        if event.key == pygame.K_SPACE:
                            self.next_quiz()

    # --------------------------
    # メインループ
    # --------------------------
    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.event()

            self.update_timer() #　更新・判定をする
    
            self.draw()
            clock.tick(60)


# ==========================
# 実行
# ==========================
if __name__ == "__main__":
    game = QuizGame()
    game.run()