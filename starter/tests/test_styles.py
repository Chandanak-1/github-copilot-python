def test_sudoku_board_region_style_variables_exist():
    with open('static/styles.css', 'r', encoding='utf-8') as styles_file:
        styles = styles_file.read()

    for variable in [f'--cell-region-bg-{index}' for index in range(9)]:
        assert variable in styles

    assert '.sudoku-cell[data-region-index="0"]' in styles
    assert '.sudoku-cell[data-region-index="8"]' in styles


def test_sudoku_board_state_styles_preserve_region_background():
    with open('static/styles.css', 'r', encoding='utf-8') as styles_file:
        styles = styles_file.read()

    assert '--cell-state-overlay' in styles
    assert '--prefilled-tint' in styles
    assert '--hinted-tint' in styles
    assert '--incorrect-tint' in styles
    assert '--conflict-tint' in styles
    assert 'box-shadow: inset 0 0 0 9999px var(--cell-state-overlay);' in styles


def test_sudoku_board_hint_style_has_background():
    with open('static/styles.css', 'r', encoding='utf-8') as styles_file:
        styles = styles_file.read()

    assert '.sudoku-cell.hinted' in styles
    assert 'background-color: var(--hinted-bg);' in styles


def test_sudoku_board_region_coloring_uses_region_index_not_cell_checkerboard():
    with open('static/main.js', 'r', encoding='utf-8') as main_js_file:
        main_js = main_js_file.read()
    with open('static/styles.css', 'r', encoding='utf-8') as styles_file:
        styles = styles_file.read()

    assert "classList.add('box-alt')" not in main_js
    assert '.sudoku-cell.box-alt' not in styles


def test_sudoku_board_region_colors_follow_checkerboard_pattern():
    with open('static/styles.css', 'r', encoding='utf-8') as styles_file:
        styles = styles_file.read()

    assert '--region-bg-light: #ffffff;' in styles
    assert '--region-bg-dark: #e9e9e9;' in styles
    assert '--cell-region-bg-0: var(--region-bg-light);' in styles
    assert '--cell-region-bg-1: var(--region-bg-dark);' in styles
    assert '--cell-region-bg-2: var(--region-bg-light);' in styles
    assert '--cell-region-bg-8: var(--region-bg-light);' in styles
