'use strict';

const e = React.createElement;

class Generation extends React.Component {
    constructor(props) {
        super(props);
        this.state = {generation: props.generation};
    }

    componentDidMount() {
        let me = this;
        socket.on('displayGeneration', function (generation) {
            me.setState({generation: generation});
        });
    }

    renderGeneration() {
        let generationList = []
        for (let i = 0; i < this.state.generation.length; i++ ) {
            generationList.push(<Board initialBoard={this.state.generation[i].boardArray} index={i}/>)
        }
        return generationList
    }

    render() {
        return (
            this.renderGeneration()
        );
    }
}

const domContainer = document.querySelector('.generation_container');
ReactDOM.render(<Generation generation={[{boardArray: [1,2,3]}]}/>, domContainer);