def test_sudoku_board_region_style_variables_exist():
    with open('static/styles.css', 'r', encoding='utf-8') as styles_file:
        styles = styles_file.read()

    assert '--cell-region-bg-0' in styles
    assert '--cell-region-bg-1' in styles
    assert '.sudoku-cell.box-alt' in styles
