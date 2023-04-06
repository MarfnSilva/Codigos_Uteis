### Create exe:
pyarmor pack --options " -D --icon integra.ico" registra_motorista.py ; copy-item ".\WXSIntegration.cfg" -Destination ".\dist\registra_motorista\"


### Descrição
Para o método /CapturaOCR utilizado na API Smart, precisamos salvar o snapshot dos eventos de LPR na pasta "\W-Access Server\Web Application\OCR". Esta integração exporta os arquivos para esta pasta, mantendo-os lá por um tempo definido no arquivo de configuração da integração.