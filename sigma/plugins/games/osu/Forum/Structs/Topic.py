from bs4 import BeautifulSoup
from .User import User
from .Post import Post


class Topic():

    def __init__(self, root, logger):
        self.root          = root
        self.logger        = logger

        self.subforum_id   = None
        self.subforum_name = None
        self.creator       = None
        self.name          = None
        self.date          = None
        self.url           = None
        self.id            = None
        self.status        = None
        self.post_roots    = None
        self.post_count    = None
        self.posts         = [ None ]


    # Overload with the Post object to ensure getTopic works for either objects
    def getTopic(self):
        return self


    def getSubforumID(self):
        if not self.subforum_id:
            try:
                subforum_url = self.root.find_all(class_='page-mode-link--is-active')[0].get('href')
                self.subforum_id = subforum_url[subforum_url.rfind('/') + 1:]
            except:
                error_msg = 'Unable to parse topic subforum id; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
        
        return self.subforum_id


    def getSubforumName(self):
        if not self.subforum_name:
            try:
                self.subforum_name = self.root.find_all(class_='page-mode-link--is-active')[0].text.strip()
            except:
                error_msg = 'Unable to parse topic subforum name; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
        
        return self.subforum_name

    
    def getDate(self):
        if not self.date:
            first_post = self.getFirstPost()
            try: self.date = first_post.getDate()
            except:
                error_msg = 'Unable to parse topic date; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
        return self.date
    
    
    def getCreator(self):
        if not self.creator:
            first_post = self.getFirstPost()
            try: self.creator = first_post.getCreator()
            except:
                error_msg = 'Unable to parse topic creator; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
        
        return self.creator

    
    # \FIXME: Apperently some threads can have no title like this one: https://osu.ppy.sh/forum/t/751805
    def getName(self):
        if not self.name:
            try:
                name = self.root.find_all(class_='js-forum-topic-title--title')[0]
                self.url  = name['href'].strip()
                self.name = name.text.strip()
            except:
                error_msg = 'Unable to parse topic name; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
           
        return self.name


    def getUrl(self):
        if not self.url:
            try:
                name = self.root.find_all(class_='js-forum-topic-title--title')[0]
                self.name = name.text.strip()
                self.url  = name['href'].strip()
            except:
                error_msg = 'Unable to parse topic url'
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
        return self.url


    def getID(self):
        if not self.id:
            url = self.getUrl()
            self.id = url[url.rfind('/') + 1:]
        
        return self.id


    # \TODO: Finish implementation
    def getStatus(self):
        if not self.status:
            # \TODO
            '''
            status = root.find_all(class_='js-forum-topic-reply--container')[0].text.strip()
            if status == 'Can not reply to a locked thread.':
                self.status = 'locked'
            else:
                self.status = 'open'
            '''
            pass

        return self.status


    def getPostCount(self):
        if not self.post_count:
            try: self.post_count = self.root.find_all(class_='js-forum__total-count')[0].text.strip().replace(',', '')
            except:
                error_msg = 'Unable to parse post count; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)

        return self.post_count


    # \TODO: Finish implementation
    @staticmethod
    def findPost(self, root, post_url):
        if len(self.posts) == 0:
            try: posts = root.find_all(class_='js-forum-post')
            except: 
                error_msg = 'Unable to parse topic posts; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)

        for post in self.getPosts(): 
            if Post(None).getUrl(post) == post_url:
                return Post(post)

        return None


    def getPostRoots(self):
        if not self.post_roots:
            try: self.post_roots = self.root.find_all(class_='js-forum-post')
            except: 
                error_msg = 'Unable to parse topic posts; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)

        return self.post_roots


    def getFirstPost(self):
        if not self.posts[0]:
            posts_root = self.getPostRoots()

            if len(posts_root) == 0:
                error_msg = 'No posts found in thread; ' + self.getUrl()
                self.logger.error(error_msg)
                raise Exception(error_msg)
        
            self.posts[0] = Post(self, posts_root[0], self.logger)

        return self.posts[0]
        


    # \TODO: Maybe this needs to be more efficient; Do only the ones that are needed to be done 
    #        and keep track of which posts were not parsed
    # Only gets visible posts (max 20)
    def getPosts(self):
        if not self.posts[0]: self.getFirstPost()
        if len(self.posts) < min(int(self.getPostCount()), 20):
            for post in self.getPostRoots()[1:]: self.posts.append(Post(self, post, self.logger))
            
        return self.posts