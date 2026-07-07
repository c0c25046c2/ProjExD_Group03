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

        # 色
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (220, 220, 220)
        self.GREEN = (120, 230, 120)
        self.RED = (255, 120, 120)

        # ゲームの状態管理 ("START", "PLAY", "RESULT")
        self.state = "START"

        # スコアと出題数の管理
        self.score = 0
        self.total_questions = 0
        self.quiz_queue = []

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
            )
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

        elif self.state == "PLAY":
            question = self.question_font.render(
                self.current_quiz.question,
                True,
                self.BLACK
            )
            self.screen.blit(question, (40, 50))

            for i in range(4):
                color = self.GRAY
                
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
                                else:
                                    answer = self.current_quiz.choices[
                                        self.current_quiz.answer
                                    ]
                                    self.message = f"不正解！ 正解は「{answer}」"

                elif self.state == "RESULT":
                    if self.retry_button.is_clicked(pos):
                        self.state = "START"

            elif event.type == pygame.KEYDOWN:
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
            self.draw()
            clock.tick(60)


# ==========================
# 実行
# ==========================
if __name__ == "__main__":
    game = QuizGame()
    game.run()