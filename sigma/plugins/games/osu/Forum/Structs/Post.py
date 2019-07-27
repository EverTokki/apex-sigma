from bs4 import BeautifulSoup
from .User import User


class Post():

    def __init__(self, topic, root, logger):
        self.topic  = topic
        self.root   = root
        self.logger = logger

        self.creator       = None
        self.date          = None
        self.post_num      = None
        self.body_root     = None
        self.contents_root = None
        self.contents      = None
        self.url           = None
        self.id            = None


    # Overload with the Topic object to ensure getTopic works for either objects
    def getTopic(self):
        return self.topic


    def getCreator(self):
        if not self.creator:
            self.creator = User(self.root)
        
        return self.creator
        

    def getDate(self):
        if not self.date:
            try:
                time = str(self.root.find_all(class_='timeago')[0]['datetime']).strip()
                self.date = parse(time)
            except:
                error_msg = 'Unable to parse post date;' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
        return self.date


    def getPostNum(self):
        if not self.post_num:
            try: self.post_num = self.topic.root.find_all(class_='js-forum-topic-post-jump--counter')[0].text.strip()
            except:
                error_msg = 'Unable to parse post number;' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)

        return self.post_num


    def getBodyRoot(self):
        if not self.body_root:
            try: self.body_root = self.root.find_all(class_='forum-post__body')[0]
            except:
                error_msg = 'Unable to parse post body;' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)

        return self.body_root
                

    def getContentsRoot(self):
        if not self.contents_root:
            try: self.contents_root = self.getBodyRoot().find_all(class_='forum-post-content ')[0]
            except:
                error_msg = 'Unable to parse post contents;' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
        
        return self.contents_root    

    
    def getContentsHTML(self): return str(self.getContentsRoot()).strip()
    def getContentsText(self): return str(self.getContentsRoot().text).strip()


    def getUrl(self):
        if not self.url:
            try: self.url = str(self.getBodyRoot().find_all(class_='js-post-url')[0]['href']).strip()
            except:
                error_msg = 'Unable to parse post url'
                self.logger.error(error_msg)
                raise Exception(error_msg)
        
        return self.url

    
    def getID(self):
        if not self.id:
            url = self.getUrl()
            self.id = url[url.rfind('/') + 1:]
        
        return self.id