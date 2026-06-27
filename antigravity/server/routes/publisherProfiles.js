import express from 'express';

export function createPublisherProfilesRouter({ readPublisherConfig, writePublisherConfig, getPublisherProfile }) {
  const router = express.Router();

  router.get('/', (req, res) => {
    res.json(readPublisherConfig());
  });

  router.put('/', (req, res) => {
    try {
      res.json(writePublisherConfig(req.body));
    } catch (err) {
      res.status(500).json({ error: '발행 프로필 저장 실패', details: err.message });
    }
  });

  router.post('/test', (req, res) => {
    const { platform, profile_id } = req.body;
    const profile = getPublisherProfile(platform, profile_id);
    if (!profile) {
      return res.status(404).json({ ok: false, error: '선택한 플랫폼 프로필을 찾을 수 없습니다.' });
    }
    if (platform === 'tistory') {
      return res.json({
        ok: Boolean(profile.blog_name && profile.access_token),
        profile,
        message: profile.blog_name && profile.access_token ? '티스토리 프로필 필수값이 준비되었습니다.' : '블로그 이름과 액세스 토큰을 입력해 주십시오.'
      });
    }
    if (platform === 'wordpress') {
      return res.json({
        ok: Boolean(profile.api_url && profile.username && profile.password),
        profile,
        message: profile.api_url && profile.username && profile.password ? '워드프레스 프로필 필수값이 준비되었습니다.' : '사이트 API 주소, 사용자명, 앱 비밀번호를 입력해 주십시오.'
      });
    }
    return res.json({ ok: true, profile, message: '프로필이 선택되었습니다.' });
  });

  return router;
}
