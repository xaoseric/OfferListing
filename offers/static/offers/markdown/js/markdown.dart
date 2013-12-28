import 'dart:html';
import 'dart:convert';
import 'dart:async';

void main(){  
  MarkdownHTMLConverter converter = new MarkdownHTMLConverter(".markdowntextfield", ".markdown-render");
  converter.refreshMarkdownContent();
}

class MarkdownHTMLConverter {
  TextAreaElement _textInput;
  DivElement _htmlOutputMaster;
  DivElement _renderedField;
  ButtonElement _refreshButton;
  ButtonElement _togglePaneButton;
  String _csrfToken;
  
  var _refreshSubscription;
  bool _renderMarkdownText;
  
  MarkdownHTMLConverter(String textAreaClass, String divOutputClass){
    _textInput = querySelectorAll(textAreaClass)[0];
    _htmlOutputMaster = querySelectorAll(divOutputClass)[0];
    _htmlOutputMaster.appendHtml('<span class="title-text">Preview</span>');
    
    /* Add new buttons */
    
    _refreshButton = new ButtonElement();
    _refreshButton.classes.addAll(["btn", "btn-success", "btn-xs"]);
    _refreshButton.text = "Refresh";
    _refreshButton.type = "button";
    _refreshButton.onClick.listen(_refreshButtonClick);
    
    _togglePaneButton = new ButtonElement();
    _togglePaneButton.classes.addAll(["btn", "btn-primary", "btn-xs"]);
    _togglePaneButton.text = "Show preview";
    _togglePaneButton.type = "button";
    _togglePaneButton.onClick.listen(_toggleButtonClick);
    
    DivElement buttonContainer = new DivElement();
    buttonContainer.append(_refreshButton);
    buttonContainer.append(_togglePaneButton);
    buttonContainer.classes.add("pull-right");
    
    _htmlOutputMaster.append(buttonContainer);
    
    /* Set up render fields */

    _renderedField = new DivElement();
    _renderedField.classes.add("render-field");

    _htmlOutputMaster.append(_renderedField);
    
    // Auto-hide preview
    hidePreview();

    // Get csrf token for post requests
    _csrfToken = querySelectorAll("[name=csrfmiddlewaretoken]")[0].value;
    
    // Set timers for rendering markdown
    _textInput.onKeyDown.listen(_textInputKeyDown);
    _textInput.onKeyUp.listen(_textInputKeyUp);
  }
  
  void _textInputKeyDown(Event e){
    _cancelMarkdownStream();
  }
  
  void _textInputKeyUp(Event e){
    _cancelMarkdownStream();
    var future = new Future.delayed(const Duration(milliseconds: 300));
    _refreshSubscription = future.asStream().listen((Stream stream) => refreshMarkdownContent());
  }
  
  void _cancelMarkdownStream(){
    if (_refreshSubscription != null){
      _refreshSubscription.cancel();
      _refreshSubscription = null;
    }
  }
  
  String getMarkdownContent(){
    return _textInput.value;
  }

  void _refreshButtonClick(Event e){
    refreshMarkdownContent();
  }
  
  void refreshMarkdownContent(){
    if (!_renderMarkdownText) return;
        
    _refreshButton.classes.add("disabled");
    var url = "/helper/markdown/";
    
    FormData requestData = new FormData();
    requestData.append("markdown", getMarkdownContent());
    requestData.append("csrfmiddlewaretoken", _csrfToken);
    
    var request = HttpRequest.request(
        url,
        method: "POST",
        sendData: requestData
    ).then(_htmlContentReceived);
  }

  void _htmlContentReceived(HttpRequest request) {
    var responseData = JSON.decode(request.responseText);
    
    NodeValidatorBuilder _htmlValidator = new NodeValidatorBuilder();
    _htmlValidator..allowHtml5()
                  ..allowImages()
                  ..allowInlineStyles()
                  ..allowSvg()
                  ..allowElement('a', attributes: ["href", "rev", "rel"])
                  ..allowElement('img', attributes: ['src']);
    
    _renderedField.setInnerHtml(responseData["html"], validator: _htmlValidator);
    _refreshButton.classes.remove("disabled");
  }
  
  void _toggleButtonClick(Event e){
    if (_renderMarkdownText){
      // Pane is currently open, close it
      hidePreview();
    } else {
      showPreview();
    }
  }
  
  void hidePreview(){
    _renderMarkdownText = false;
    
    _refreshButton.classes.add("disabled");
    _renderedField.hidden = true;
    
    _togglePaneButton.text = "Show preview";
    _togglePaneButton.classes.remove("btn-info");
    _togglePaneButton.classes.add("btn-primary");
  }
  
  void showPreview(){
    _renderMarkdownText = true;
    refreshMarkdownContent();
    
    _renderedField.hidden = false;
    
    _togglePaneButton.text = "Hide preview";
    _togglePaneButton.classes.remove("btn-primary");
    _togglePaneButton.classes.add("btn-info");
  }
}
