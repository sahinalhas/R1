import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { DashboardStats } from '../types';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <Container className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h2>Dashboard</h2>
            <div>
              <span className="me-3">Hoş geldin, {user?.tam_ad}</span>
              <Button variant="outline-secondary" onClick={handleLogout}>
                Çıkış Yap
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {loading ? (
        <Row>
          <Col>
            <Card>
              <Card.Body className="text-center">
                <p>İstatistikler yükleniyor...</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ) : (
        <Row>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="text-primary">{stats?.ogrenci_sayisi || 0}</h3>
                <p className="mb-0">Toplam Öğrenci</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="text-success">{stats?.bu_ay_gorusme_sayisi || 0}</h3>
                <p className="mb-0">Bu Ay Görüşme</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="text-warning">{stats?.bu_ay_etkinlik_sayisi || 0}</h3>
                <p className="mb-0">Bu Ay Etkinlik</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="text-info">{stats?.ortalama_ilerleme || 0}%</h3>
                <p className="mb-0">Ortalama İlerleme</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>
              <h5>Hızlı Erişim</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2 d-md-flex justify-content-md-start">
                <Button variant="primary" className="me-md-2">
                  Yeni Öğrenci Ekle
                </Button>
                <Button variant="success" className="me-md-2">
                  Görüşme Kaydet
                </Button>
                <Button variant="warning" className="me-md-2">
                  Etkinlik Oluştur
                </Button>
                <Button variant="info">
                  Rapor Görüntüle
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;