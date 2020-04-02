'use strict';

const e = React.createElement;
let initialBoard = 
    [[5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]];

class Board extends React.Component {
    constructor(props) {
        super(props);
        this.board = props.initialBoard;
        this.index = props.index;
    }



    renderTableRows() {
        let tableRows = []
        for (let i = 0; i < this.board.length; i++) {
            let row = []
            for (let j = 0; j < this.board[i].length; j++) {
                row.push(<Cell row={i} col={j} value={this.board[i][j]}/>)
            }
            tableRows.push(<tr>{row}</tr>)
        }
        return tableRows
    }

    render() {
        return (
            <table>
                {this.renderTableRows()}
            </table>
        );
    }
}