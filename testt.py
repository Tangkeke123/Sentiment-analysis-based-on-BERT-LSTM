import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 14))
ax.set_xlim(0, 10)
ax.set_ylim(0, 16)
ax.axis('off')


def draw_box(x, y, width, height, text, color='lightblue'):
    rect = plt.Rectangle((x, y), width, height, fc=color, ec='black', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + width / 2, y + height / 2, text, ha='center', va='center', fontsize=9, weight='bold')


# 卷积层
layers = [
    (3, 15, "conv1\n64"), (5.5, 15, "conv1\n64"),
    (3, 13.5, "conv2\n64"), (5.5, 13.5, "conv2\n64"),
    (2.5, 12, "conv3\n256"), (4.5, 12, "conv3\n256"), (6.5, 12, "conv3\n256"),
    (2.5, 10.5, "conv4\n512"), (4.5, 10.5, "conv4\n512"), (6.5, 10.5, "conv4\n512"),
    (2.5, 9, "conv5\n512"), (4.5, 9, "conv5\n512"), (6.5, 9, "conv5\n512"),
]

for x, y, text in layers:
    draw_box(x, y, 1.8, 0.9, text, 'lightcoral')

# 全连接层
draw_box(3.5, 7, 2.5, 0.9, "fc to conv\n8000", 'lightgreen')
draw_box(3.5, 5.5, 2.5, 0.9, "fe8 to conv\nK", 'lightgreen')

# 多个 K 层
for i in range(4):
    y = 4 - i * 1.2
    draw_box(3.5, y, 2.5, 0.9, f"全连接层\nK", 'lightyellow')

draw_box(3.5, 0.5, 2.5, 0.9, "Softmax", 'gold')
draw_box(3.5, -0.8, 2.5, 0.9, "输出 K 类", 'gold')


# 箭头
def add_arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', lw=1.5))


# 同一行内部箭头
add_arrow(4.8, 15.45, 5.5, 15.45)
add_arrow(4.8, 13.95, 5.5, 13.95)
add_arrow(4.3, 12.45, 4.5, 12.45)
add_arrow(6.3, 12.45, 6.5, 12.45)
# 跨行箭头
add_arrow(4.8, 14.55, 3.9, 13.95)
add_arrow(4.8, 13.05, 3.9, 12.45)
add_arrow(4.8, 11.55, 3.9, 10.95)
add_arrow(4.8, 10.05, 3.9, 9.45)
add_arrow(4.8, 8.55, 4.75, 7.45)
add_arrow(4.8, 6.95, 4.75, 5.95)
for i in range(3):
    add_arrow(4.8, 5.05 - i * 1.2, 4.75, 3.85 - i * 1.2)
add_arrow(4.8, 0.95, 4.75, 0.05)
add_arrow(4.8, -0.35, 4.75, -0.35)

plt.tight_layout()
plt.savefig('cnn_structure.png', dpi=300, bbox_inches='tight')
plt.show()
