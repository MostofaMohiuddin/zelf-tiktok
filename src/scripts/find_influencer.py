from src.database.author_repository import AuthorRepository
from src.models.user import User


class IdentifyInfluencer:
    def __init__(self) -> None:
        self.author_repository = AuthorRepository()

    def find(self) -> list[User]:
        influencer = self.author_repository.get_influencer()
        for user in influencer:
            print(user.tiktok_unique_id, user.follower_count, user.like_count)
        print(f"Total influencer found: {len(influencer)}")
        return influencer


if __name__ == "__main__":
    IdentifyInfluencer().find()
