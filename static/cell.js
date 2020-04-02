'use strict';

const e = React.createElement;

class Cell extends React.Component {
    constructor(props) {
        super(props);
        this.row = props.row;
        this.col = props.col;
        this.state = { value: props.value, changed: false };
    }

    componentDidMount() {
        let me = this;
        socket.on('cellChange', function (row, col, possibleNumber) {
            if (me.row == row && me.col == col) {
                me.setState({ value: possibleNumber, changed: true });
            }
        });
    }

    render() {
        return (
            <td className={this.state.changed ? 'changed' : ''}>
                {this.state.value}
            </td>
        );
    }
}