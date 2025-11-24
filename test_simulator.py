"""
Testes unitários para o simulador
Execute com: python -m pytest test_simulator.py
ou: python test_simulator.py
"""

import unittest
from MemoryConfig import MemoryConfig
from TLB import TLB
from PageTableEntry import PageTable
from PhysicalMemory import PhysicalMemory
from SegmentManager import SegmentManager
from mmu import MMU


class TestMemoryConfig(unittest.TestCase):
    """Testes para a configuração do sistema"""

    def test_config_default(self):
        """Testa configuração padrão"""
        config = MemoryConfig()
        self.assertEqual(config.tlb_entries, 4)
        self.assertEqual(config.virtual_addr_space, 65536)
        self.assertEqual(config.physical_memory_size, 16384)
        self.assertEqual(config.page_size, 1024)

    def test_config_custom(self):
        """Testa configuração personalizada"""
        config = MemoryConfig(
            tlb_entries_bits=3,
            virtual_addr_bits=18,
            physical_addr_bits=16
        )
        self.assertEqual(config.tlb_entries, 8)
        self.assertEqual(config.virtual_addr_space, 262144)
        self.assertEqual(config.physical_memory_size, 65536)

    def test_invalid_config(self):
        """Testa configuração inválida"""
        with self.assertRaises(ValueError):
            MemoryConfig(virtual_addr_bits=12, physical_addr_bits=14)


class TestTLB(unittest.TestCase):
    """Testes para a TLB"""

    def setUp(self):
        self.tlb = TLB(4)

    def test_tlb_miss(self):
        result = self.tlb.lookup(10)
        self.assertIsNone(result)
        self.assertEqual(self.tlb.misses, 1)

    def test_tlb_hit(self):
        self.tlb.insert(10, 5)
        result = self.tlb.lookup(10)
        self.assertEqual(result, 5)
        self.assertEqual(self.tlb.hits, 1)

    def test_tlb_replacement(self):
        # Preenche a TLB
        for i in range(4):
            self.tlb.insert(i, i * 10)

        # Insere mais um (deve substituir o primeiro)
        self.tlb.insert(4, 40)

        self.assertIsNone(self.tlb.lookup(0))
        self.assertEqual(self.tlb.lookup(4), 40)


class TestPageTable(unittest.TestCase):
    """Testes para a tabela de páginas"""

    def test_single_level(self):
        config = MemoryConfig(page_table_levels=1)
        pt = PageTable(config)

        pt.insert(10, 5)
        result = pt.lookup(10)
        self.assertEqual(result, 5)

    def test_two_levels(self):
        config = MemoryConfig(page_table_levels=2)
        pt = PageTable(config)

        pt.insert(20, 7)
        result = pt.lookup(20)
        self.assertEqual(result, 7)

    def test_three_levels(self):
        config = MemoryConfig(page_table_levels=3)
        pt = PageTable(config)

        pt.insert(30, 12)
        result = pt.lookup(30)
        self.assertEqual(result, 12)

    def test_lookup_not_found(self):
        config = MemoryConfig()
        pt = PageTable(config)
        result = pt.lookup(999)
        self.assertEqual(result, -1)

    def test_invalidate(self):
        config = MemoryConfig(page_table_levels=2)
        pt = PageTable(config)

        pt.insert(15, 3)
        self.assertEqual(pt.lookup(15), 3)

        pt.invalidate(15)
        self.assertEqual(pt.lookup(15), -1)


class TestPhysicalMemory(unittest.TestCase):
    """Testes para a memória física"""

    def setUp(self):
        self.memory = PhysicalMemory(4)

    def test_allocate_frame(self):
        frame, evicted_vpn = self.memory.allocate_frame(0x1000)
        self.assertEqual(frame, 0)
        self.assertIsNone(evicted_vpn)
        self.assertEqual(self.memory.page_faults, 1)

    def test_lru_replacement(self):
        for i in range(4):
            self.memory.allocate_frame(i * 0x1000)

        self.memory.update_access(1)
        self.memory.update_access(2)
        self.memory.update_access(3)

        frame, evicted_vpn = self.memory.allocate_frame(0x5000)
        self.assertEqual(frame, 0)
        self.assertIsNotNone(evicted_vpn)
        self.assertEqual(self.memory.page_replacements, 1)


class TestSegmentManager(unittest.TestCase):
    """Testes para o gerenciador de segmentos"""

    def setUp(self):
        self.config = MemoryConfig()
        self.segment_mgr = SegmentManager(self.config)

    def test_identify_text_segment(self):
        segment = self.segment_mgr.identify_segment(0x0000)
        self.assertEqual(segment, 'text')

    def test_identify_data_segment(self):
        segment = self.segment_mgr.identify_segment(0x1000)
        self.assertEqual(segment, 'data')

    def test_identify_stack_segment(self):
        segment = self.segment_mgr.identify_segment(0xF800)
        self.assertEqual(segment, 'stack')

    def test_invalid_address(self):
        segment = self.segment_mgr.identify_segment(self.config.virtual_addr_space + 100)
        self.assertIsNone(segment)


class TestMMU(unittest.TestCase):
    """Testes para a MMU"""

    def setUp(self):
        self.config = MemoryConfig()
        self.mmu = MMU(self.config)

    def test_first_translation(self):
        trans = self.mmu.translate(0x0000)
        self.assertEqual(trans.vpn, 0)
        self.assertTrue(trans.page_fault)
        self.assertFalse(trans.tlb_hit)

    def test_second_access_tlb_hit(self):
        self.mmu.translate(0x0000)
        trans = self.mmu.translate(0x0010)
        self.assertTrue(trans.tlb_hit)
        self.assertFalse(trans.page_fault)

    def test_invalid_address(self):
        with self.assertRaises(ValueError):
            self.mmu.translate(self.config.virtual_addr_space + 1)

    def test_statistics(self):
        for i in range(10):
            self.mmu.translate(i * 0x400)

        stats = self.mmu.get_statistics()
        self.assertEqual(stats['total_translations'], 10)
        self.assertGreater(stats['page_faults'], 0)


class TestIntegration(unittest.TestCase):
    """Testes de integração"""

    def test_full_workflow(self):
        config = MemoryConfig()
        mmu = MMU(config)

        addresses = [0x0000, 0x0400, 0x0800, 0x0010, 0x0420]
        translations = [mmu.translate(a) for a in addresses]

        self.assertEqual(len(translations), 5)

        stats = mmu.get_statistics()
        self.assertEqual(stats['total_translations'], 5)


def run_tests():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
