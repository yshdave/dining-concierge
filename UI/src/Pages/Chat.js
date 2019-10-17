import React from 'react';
import _ from 'lodash';
import './Chat.css';
import { FaArrowCircleUp } from 'react-icons/fa';
import apigClientFactory from 'aws-api-gateway-client';

class Chat extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      draft: '',
      chatHistory: []
    }

    this.apigClient = apigClientFactory.newClient({
      invokeUrl: "https://tzjt9w01p1.execute-api.us-east-1.amazonaws.com/development/chatbot"
    });
  }

  generateBotResponse(text) {
    if (!text || text.length === 0) {
      return;
    }
    let { chatHistory } = this.state;
    chatHistory.push({ text, sender: 'bot' });
    this.setState({ chatHistory });
  }
  contactLex() {
    const pathParams = {};
    const pathTemplate = ''
    const additionalParams = {
      queryParams: {
        'user_message': this.state.draft
      }
    }
    this.apigClient.invokeApi(pathParams, pathTemplate, 'GET', additionalParams)
      .then((result) => {
        this.generateBotResponse(result.data);
      })
      .catch((err) => {
        this.generateBotResponse('something went wrong');
      })

  }
  handleUserInput() {
    let { chatHistory, draft } = this.state;
    if (!draft || draft.length === 0) {
      return;
    }
    chatHistory.push({ text: draft, sender: 'user' });
    this.setState({ chatHistory, draft: '' });
    this.contactLex();
  }

  updateDraft(event) {
    this.setState({ draft: event.target.value });
  }

  handleEnter(event) {
    if (event.key === 'Enter') {
      this.handleUserInput();
    }
  }

  renderChatHistory() {
    const { chatHistory } = this.state;
    const chatComponent = []
    _.each(chatHistory, ({ text, sender }) => {
      const chatBubbleOrientation = sender === 'bot' ? 'align-self-start' : 'align-self-end';
      const chatBubbleColor = sender === 'bot' ? 'bg-secondary' : 'bg-primary';
      chatComponent.unshift(
        <div class={`card chat-bubble mb-2  ${chatBubbleOrientation} ${chatBubbleColor}`}>
          <div class="card-body d-flex  pt-1 pb-1 pl-2 pr-2">
            {text}
          </div>
        </div>
      )
    });
    return chatComponent;
  }


  render() {
    return (
      <div className="container  h-100">
        <div className="row chat-area h-100 pt-1 pb-1">
          <div className="fill col col-md-6 offset-md-3   col-sm-12 col-lg-4 offset-lg-4 border d-flex flex-column justify-content-between shadow-lg rounded-corners bg-white">
            <div className="chat-header mt-3 font-weight-bold d-flex justify-content-center align-items-center border-bottom">
              <h4>Chatbot</h4>
            </div>
            <div className="chat-content d-flex flex-column-reverse justify-content-end fill pt-2 pb-2">
              <div className=" d-flex flex-column-reverse  scroller-div fill">
                {this.renderChatHistory()}
              </div>
            </div>
            <div className="chat-footer d-flex pb-2 pt-2 mb-2 border-top align-items-center">
              <div class="input-group mr-2">
                <input
                  type="text"
                  class="form-control"
                  value={this.state.draft}
                  onChange={this.updateDraft.bind(this)}
                  onKeyDown={this.handleEnter.bind(this)}
                ></input>
              </div>
              <div className="send-button" onClick={this.handleUserInput.bind(this)}>
                <FaArrowCircleUp className="text-primary" fontSize="xx-large" />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Chat;