"""Top-level simulator that composes TLB, PageTable, PhysicalMemory, Segments.
Produces separate output files:
 - tlb_out.txt (contents of TLB)
 - pagetable_out.txt (page table mappings)
 - physmem_out.txt (physical frames dump)
 - simulator_out.txt (per-access trace and stats)
"""
import argparse
from tlb import TLB
from pagetable import PageTable
from physmem import PhysicalMemory
from segments import compute_segments, which_segment

def read_addresses(path: str):
    addrs = []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s: continue
            try:
                if s.startswith("0x") or s.startswith("0X"):
                    addrs.append(int(s,16))
                else:
                    addrs.append(int(s))
            except:
                continue
    return addrs

def write_tlb_out(path, tlb):
    with open(path, "w") as f:
        f.write("VPN\tPFN\ttime_added\n")
        for vpn,pfn,time in tlb.dump():
            f.write(f"{vpn}\t{pfn}\t{time}\n")

def write_pagetable_out(path, pt):
    with open(path, "w") as f:
        f.write("VPN -> PFN\n")
        for vpn,pfn in sorted(pt.dump_mappings().items()):
            f.write(f"{vpn} -> {pfn}\n")

def write_phys_out(path, pm):
    with open(path, "w") as f:
        f.write("FrameIndex -> VPN(-1 free)\n")
        for i, v in enumerate(pm.dump()):
            f.write(f"{i} -> {v}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tlb-bits", type=int, default=3, help="TLB entries = 2^bits (0..6 allowed)")
    parser.add_argument("--virt-bits", type=int, default=16)
    parser.add_argument("--phys-bits", type=int, default=14)
    parser.add_argument("--page-bits", type=int, default=8)
    parser.add_argument("--seg-text-bits", type=int, default=10)
    parser.add_argument("--seg-data-bits", type=int, default=10)
    parser.add_argument("--seg-stack-bits", type=int, default=10)
    parser.add_argument("--pt-levels", type=int, default=1, choices=[1,2,3])
    parser.add_argument("--infile", type=str, default="enderecos.txt")
    parser.add_argument("--out-prefix", type=str, default="out")
    args = parser.parse_args()

    page_size = 1 << args.page_bits
    virtual_size = 1 << args.virt_bits
    physical_size = 1 << args.phys_bits
    num_pages = virtual_size // page_size
    num_frames = physical_size // page_size
    vpn_bits = args.virt_bits - args.page_bits

    tlb = TLB(entries_bits=args.tlb_bits)
    pt = PageTable(vpn_bits=vpn_bits, levels=args.pt_levels)
    pm = PhysicalMemory(num_frames=num_frames)
    segments = compute_segments(virtual_size, 1<<args.seg_text_bits, 1<<args.seg_data_bits, 1<<args.seg_stack_bits)

    addresses = read_addresses(args.infile)
    if len(addresses)==0:
        print("No addresses in file")
        return

    time = 0
    accesses = []
    page_faults = 0
    evictions = 0

    for v in addresses:
        if v < 0 or v >= virtual_size:
            raise ValueError(f"Address {v} out of range [0,{virtual_size-1}]")
        vpn = v // page_size
        offset = v % page_size
        seg = which_segment(segments, v)
        # TLB lookup
        pfn = tlb.lookup(vpn)
        tlb_hit = False
        pfault = False
        if pfn is not None:
            tlb_hit = True
            pm.touch(pfn)
            paddr = pfn*page_size + offset
        else:
            # check page table
            pfn = pt.lookup(vpn)
            if pfn == -1:
                # page fault -> allocate
                page_faults += 1
                frame_idx, evicted_vpn = pm.allocate(vpn)
                if evicted_vpn is not None:
                    pt.unmap(evicted_vpn)
                    tlb.invalidate(evicted_vpn)
                    evictions += 1
                pt.map(vpn, frame_idx)
                tlb.add(vpn, frame_idx, time)
                pm.touch(frame_idx)
                pfn = frame_idx
                pfault = True
            else:
                tlb.add(vpn, pfn, time)
                pm.touch(pfn)
            paddr = pfn*page_size + offset
        accesses.append((v, seg, paddr, tlb_hit, pfault))
        time += 1

    # write separate outputs
    out_prefix = args.out_prefix
    write_tlb_out(f"{out_prefix}_tlb.txt", tlb)
    write_pagetable_out(f"{out_prefix}_pagetable.txt", pt)
    write_phys_out(f"{out_prefix}_physmem.txt", pm)
    with open(f"{out_prefix}_simulator.txt","w") as f:
        f.write("Virtual\tSegment\tPhysical\tTLB_hit\tPageFault\n")
        for a in accesses:
            f.write(f"{a[0]}\t{a[1]}\t{a[2]}\t{a[3]}\t{a[4]}\n")
        f.write("\n-- Stats --\n")
        f.write(f"Accesses: {len(accesses)}\n")
        f.write(f"PageFaults: {page_faults}\n")
        f.write(f"Evictions: {evictions}\n")
        f.write(f"TLB entries (max): {tlb.size}\n")
        f.write(f"Num pages: {num_pages}\n")
        f.write(f"Num frames: {num_frames}\n")

if __name__ == '__main__':
    main()
