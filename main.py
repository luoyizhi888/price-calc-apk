from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock

import re
import datetime

# ---------- 核心计算函数（与原代码一致） ----------
def format_number(num):
    num_str = str(num)
    if '.' in num_str and len(num_str.split('.')[1]) > 3:
        return round(num, 2)
    return num

def safe_eval(expr):
    try:
        allowed_chars = set('0123456789+-*/. ()')
        if not all(c in allowed_chars for c in expr):
            return 0
        return eval(expr)
    except:
        return 0

def calculate_product_count(expr):
    expr_clean = expr.replace(' ', '')
    pattern = r'(\d+(?:\.\d+)?)(?:\*(\d+(?:\.\d+)?))?'
    matches = re.findall(pattern, expr_clean)
    total_count = 0
    for match in matches:
        if match[1]:
            count = float(match[1])
        else:
            count = 1
        total_count += count
    if total_count % 1 == 0:
        total_count = int(total_count)
    return total_count

def calculate_result(price_expr, shipping_expr):
    """返回 (detail_str, result_str) 以便显示和复制"""
    # 替换中文括号
    price_expr = price_expr.replace('（', '(').replace('）', ')')
    shipping_expr = shipping_expr.replace('（', '(').replace('）', ')')

    a_value = safe_eval(price_expr)
    if a_value == 0 and price_expr != '0':
        return None, "价格表达式无效"

    a_formatted = format_number(a_value)
    b_formatted = format_number(safe_eval(shipping_expr)) if shipping_expr else 0
    total_formatted = format_number(a_formatted + b_formatted)

    n = calculate_product_count(price_expr)

    # 处理价格表达式中的$符号
    a_expr_clean = price_expr.replace(' ', '')
    a_expr_modified = re.sub(r'\+([^$])', r'+$\1', a_expr_clean)

    # 格式化整数
    if isinstance(a_formatted, float) and a_formatted % 1 == 0:
        a_formatted = int(a_formatted)
    if isinstance(b_formatted, float) and b_formatted % 1 == 0:
        b_formatted = int(b_formatted)
    if isinstance(total_formatted, float) and total_formatted % 1 == 0:
        total_formatted = int(total_formatted)

    # 构建详细字符串（用于显示和复制）
    lines = []
    if b_formatted:
        lines.append(f'总计:${total_formatted}（${a_formatted} + ${b_formatted}）\n')
    else:
        lines.append(f'总计:${total_formatted}\n')
    lines.append('-' * 17 + '\n')

    if str(a_expr_modified) == str(a_formatted):
        lines.append(f'{n}件产品价格: ${a_formatted}\n')
    else:
        lines.append(f'{n}件产品价格: ${a_expr_modified} = ${a_formatted}\n')

    if b_formatted:
        lines.append(f'运费: ${b_formatted}\n')

    detail_str = ''.join(lines)
    # result_str 和 detail_str 一样（可根据需要调整）
    return detail_str, detail_str
# ---------- 核心函数结束 ----------

class CalculatorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        # 价格输入
        self.add_widget(Label(text='产品价格:', size_hint_y=None, height=40))
        self.price_input = TextInput(hint_text='例如: 38.47*2', multiline=False, font_size='18sp')
        self.add_widget(self.price_input)

        # 运费输入
        self.add_widget(Label(text='运    费:', size_hint_y=None, height=40))
        self.shipping_input = TextInput(hint_text='例如: 35', multiline=False, font_size='18sp')
        self.add_widget(self.shipping_input)

        # 按钮
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        calc_btn = Button(text='计算并复制', font_size='18sp')
        calc_btn.bind(on_press=self.calc_and_copy)
        btn_layout.add_widget(calc_btn)

        clear_btn = Button(text='清空', font_size='18sp')
        clear_btn.bind(on_press=self.clear_inputs)
        btn_layout.add_widget(clear_btn)
        self.add_widget(btn_layout)

        # 结果显示区域（可滚动）
        scroll = ScrollView()
        self.result_label = Label(text='等待输入...', size_hint_y=None, font_size='16sp', halign='left', valign='top')
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        scroll.add_widget(self.result_label)
        self.add_widget(scroll)

        # 状态栏
        self.status = Label(text='就绪', size_hint_y=None, height=30, font_size='14sp')
        self.add_widget(self.status)

    def calc_and_copy(self, instance):
        price = self.price_input.text.strip()
        shipping = self.shipping_input.text.strip()
        if not price:
            self.status.text = '请输入产品价格'
            return

        detail, _ = calculate_result(price, shipping)
        if detail is None:
            self.status.text = '价格表达式无效'
            return

        # 显示结果
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        display_text = f"{'='*22}\n当前计算结果 ({current_time}):\n{'='*22}\n{detail}"
        self.result_label.text = display_text

        # 复制到剪贴板
        Clipboard.copy(detail.strip())
        self.status.text = f'✓ 结果已复制到剪贴板'

    def clear_inputs(self, instance):
        self.price_input.text = ''
        self.shipping_input.text = ''
        self.result_label.text = ''
        self.status.text = '输入框已清空'

class PriceCalcApp(App):
    def build(self):
        return CalculatorLayout()

if __name__ == '__main__':
    PriceCalcApp().run()